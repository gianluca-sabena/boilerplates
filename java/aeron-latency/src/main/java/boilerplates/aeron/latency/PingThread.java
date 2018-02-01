package boilerplates.aeron.latency;
/*
 * Copyright 2014-2017 Real Logic Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import io.aeron.*;
import org.HdrHistogram.Histogram;
import io.aeron.logbuffer.FragmentHandler;
import io.aeron.logbuffer.Header;
import org.agrona.BitUtil;
import org.agrona.BufferUtil;
import org.agrona.DirectBuffer;
import org.agrona.concurrent.BusySpinIdleStrategy;
import org.agrona.concurrent.IdleStrategy;
import org.agrona.concurrent.UnsafeBuffer;

import java.util.concurrent.*;

import io.aeron.samples.SampleConfiguration;


/**
 * Ping component of Ping-Pong latency test.
 * <p>
 * Initiates and records times.
 */
public class PingThread {
  private static final int PING_STREAM_ID = SampleConfiguration.PING_STREAM_ID;
  private static final int PONG_STREAM_ID = SampleConfiguration.PONG_STREAM_ID;
  private static final long NUMBER_OF_MESSAGES = SampleConfiguration.NUMBER_OF_MESSAGES;
  private static final int MESSAGE_LENGTH = SampleConfiguration.MESSAGE_LENGTH;
  private static final int FRAGMENT_COUNT_LIMIT = SampleConfiguration.FRAGMENT_COUNT_LIMIT;
  private static final boolean EMBEDDED_MEDIA_DRIVER = SampleConfiguration.EMBEDDED_MEDIA_DRIVER;
  private static final String PING_CHANNEL = SampleConfiguration.PING_CHANNEL;
  private static final String PONG_CHANNEL = SampleConfiguration.PONG_CHANNEL;
  private static final String MEDIA_DRIVER_FOLDER = System.getProperty("aeron.media.driver.folder", "/tmp/aeron-media-driver");

  private static final CountDownLatch LATCH = new CountDownLatch(1);

  public static void main(final String[] args) throws Exception {
    final ExecutorService executor = Executors.newFixedThreadPool(4);


    final Aeron.Context ctx = new Aeron.Context().availableImageHandler(PingThread::availablePongImageHandler);
    if (EMBEDDED_MEDIA_DRIVER)
    {
      ctx.aeronDirectoryName(MEDIA_DRIVER_FOLDER);
    }


    System.out.println("Publishing Ping at " + PING_CHANNEL + " on stream Id " + PING_STREAM_ID);
    System.out.println("Subscribing Pong at " + PONG_CHANNEL + " on stream Id " + PONG_STREAM_ID);
    System.out.println("Message length of " + MESSAGE_LENGTH + " bytes");

    try (Aeron aeron = Aeron.connect(ctx)) {


      try (Publication publication = aeron.addPublication(PING_CHANNEL, PING_STREAM_ID);
           Subscription subscription = aeron.addSubscription(PONG_CHANNEL, PONG_STREAM_ID)) {
        LATCH.await();

        for(int i = 0; i<3;i++){
          Sender sender = new Sender(publication);
          Receiver receiver = new Receiver(subscription);
          System.out.println("--- --- Iteration:" + i +" --- ---");
          Future<?> receiverFuture = executor.submit(receiver);
          Future<?> senderFuture = executor.submit(sender);
          senderFuture.get();
          receiverFuture.get();
          Thread.sleep(1000);
        }
        executor.shutdown();
        executor.awaitTermination(30L, TimeUnit.SECONDS);
      }
    }
    ctx.close();
  }

  private static class Sender implements Runnable {
    private static final BusySpinIdleStrategy OFFER_IDLE_STRATEGY = new BusySpinIdleStrategy();
    private Publication publication;
    private static final UnsafeBuffer ATOMIC_BUFFER = new UnsafeBuffer(
        BufferUtil.allocateDirectAligned(MESSAGE_LENGTH, BitUtil.CACHE_LINE_LENGTH));

    public Sender(Publication pub) {
      publication = pub;
    }

    public void run() {
      System.out.println("Start sender!");

      long backPressureCount = 0;
      OFFER_IDLE_STRATEGY.reset();
      for (long i = 0; i < NUMBER_OF_MESSAGES ; i++) {
        ATOMIC_BUFFER.putLong(0, System.nanoTime());
        //ATOMIC_BUFFER.putLong(8, i);
        long code = -100;
        while (code < 0L) {
          code = publication.offer(ATOMIC_BUFFER, 0, MESSAGE_LENGTH);
//          if (code < 0L) {
//            System.out.println("Sender offer error: " + code);
//          }
          // The offer failed, which is usually due to the publication
          // being temporarily blocked.  Retry the offer after a short
          // spin/yield/sleep, depending on the chosen IdleStrategy.
          backPressureCount++;
          OFFER_IDLE_STRATEGY.idle();
        }

      }

      System.out.println(
          "Done streaming. Back pressure ratio " + ((double) backPressureCount / NUMBER_OF_MESSAGES));
      return;
    }
  }

  private static class Receiver implements Runnable {
    private Subscription subscription;
    private static int receivedMsg;
    private static final IdleStrategy POLLING_IDLE_STRATEGY = new BusySpinIdleStrategy();
    private static final Histogram histogram = new Histogram(TimeUnit.SECONDS.toNanos(10), 3);
    public Receiver(Subscription sub) {
      subscription = sub;
    }


    public void run() {
      System.out.println("Start receiver!");
      histogram.reset();
      receivedMsg = 0;
      final long startTs = System.nanoTime();
      POLLING_IDLE_STRATEGY.reset();
      final FragmentHandler fragmentHandler = new FragmentAssembler(Receiver::pongHandler);
      while (!subscription.isConnected()) {
        Thread.yield();
      }
      final Image image = subscription.imageAtIndex(0);

      while (!Thread.currentThread().isInterrupted() && receivedMsg < NUMBER_OF_MESSAGES ) {
        int fragments = image.poll(fragmentHandler, FRAGMENT_COUNT_LIMIT);
        POLLING_IDLE_STRATEGY.idle(fragments);
      }
      System.out.println(" STOP RECEIVER");
      histogram.outputPercentileDistribution(System.out, 1000.0);

      final long elapsed = Math.round((System.nanoTime() - startTs) / 1000000);
      final float rate = receivedMsg / elapsed * 1000f;
      final float th = rate * ((float) MESSAGE_LENGTH / 1024f / 1024f);
      System.out.println(" Elapsed time: " + elapsed + " ms - Messages: " + receivedMsg + " Size: " + MESSAGE_LENGTH + " byte");
      System.out.printf(" Rate: %f msg/s - Data: %f MB/s \n", rate, th);
      return;
    }

    private static void pongHandler(final DirectBuffer buffer, final int offset, final int length, final Header header) {
      receivedMsg++;
      final long pingTimestamp = buffer.getLong(offset);
      final long rttNs = System.nanoTime() - pingTimestamp;
      //System.out.println("Msg lat: "+rttNs);
      histogram.recordValue(rttNs);
    }
  }


  private static void availablePongImageHandler(final Image image) {
    final Subscription subscription = image.subscription();
    System.out.format(
        "Available image: channel=%s streamId=%d session=%d%n",
        subscription.channel(), subscription.streamId(), image.sessionId());

    if (PONG_STREAM_ID == subscription.streamId() && PONG_CHANNEL.equals(subscription.channel())) {
      LATCH.countDown();
    }
  }
}

