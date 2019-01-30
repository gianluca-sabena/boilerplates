/**
 * From https://www.baeldung.com/java-completablefuture
 */
package com.boilerplates;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import io.reactivex.Observable;

class SimpleFuture {
  private static ExecutorService executor = Executors.newCachedThreadPool();

  public void close() throws InterruptedException {
    executor.shutdown();
    executor.awaitTermination(30, TimeUnit.SECONDS);
  }

  public void combine() throws InterruptedException, ExecutionException {
    CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello");
    CompletableFuture<String> future = completableFuture.thenApply(s -> s + " World");
    System.out.println("Output form combine(): " + future.get());
  }

  public void run() throws InterruptedException, ExecutionException {
    combine();
    CompletableFuture<String> future1 = calculateAsync("Hello", 500);
    /**
     * thenApply and thenCompose explained https://www.baeldung.com/java-completablefuture#Combining
     */
    CompletableFuture<String> future2 = future1.thenApply(s -> s + " And then another future!");
    CompletableFuture<Integer> future3 = future2.thenApply(s -> s.length());
    CompletableFuture<String> future4 =
        future3.thenCompose(s -> CompletableFuture.supplyAsync(() -> "Length is " + s.toString()));

    CompletableFuture<Void> futureA =
        future2.thenAccept(s -> System.out.println("Computation returned: " + s));
    CompletableFuture<Void> futureB =
        future3.thenAccept(s -> System.out.println("Computation returned: " + s));
    CompletableFuture<Void> futureC =
        future4.thenAccept(s -> System.out.println("Computation returned: " + s));

    // whait all futures, but doesn't combine results
    CompletableFuture<Void> combined1 = CompletableFuture
        .allOf(calculateAsync("combined1 Parallel 1", 500),
            calculateAsync("combined1 Parallel 2", 700))
        .thenAccept((s) -> System.out.println("combined1 finished"));
    // how to run in parallel and join
    String combined3 = Stream.of(calculateAsync("combined3 Parallel 1", 500),
        calculateAsync("combined3 Parallel 2", 100), calculateAsync("combined3 Parallel 3", 700))
        .map(CompletableFuture::join) // similar to get so it blocks on parallel 1 also if parallel2
                                      // is faster - see RxJava on how to solve this!
        .collect(Collectors.joining(", "));
    System.out.println("combined3 returned: " + combined3);

    close();
  }


  private CompletableFuture<String> calculateAsync(String msg, Integer sleep)
      throws InterruptedException {
    String id = "- id: msg_" + msg + "_" + sleep + "_ms";
    CompletableFuture<String> completableFuture = new CompletableFuture<>();
    executor.submit(() -> {
      System.out.println("calculateAsync - Start "+id);
      Thread.sleep(sleep);
      completableFuture.complete("calculateAsync - Complete future "+id);
      System.out.println("calculateAsync - End "+id);
      return null;
    });

    return completableFuture;
  }
}
