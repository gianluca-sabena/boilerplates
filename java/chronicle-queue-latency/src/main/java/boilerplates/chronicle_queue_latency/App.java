package boilerplates.chronicle_queue_latency;

import java.io.IOException;

public class App {
  public static void main(String[] args) throws IOException, InterruptedException {
    int throughtput = 50_000; // msg / sec
    int messages = 10_000_000;
    System.out.println("Start latency test...");
    System.out.println("Estimated time: " + messages / throughtput + " seconds");
    LatencyFromTest latencyFromTest = new LatencyFromTest();
    try {
      latencyFromTest.run(throughtput, messages);
    } catch (IOException e) {
      e.printStackTrace();
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
  }
}
