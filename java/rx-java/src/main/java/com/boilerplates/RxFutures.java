/**
 * From https://www.baeldung.com/java-completablefuture
 */
package com.boilerplates;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import io.reactivex.Observable;

class RxFuture {
  private static ExecutorService executor = Executors.newFixedThreadPool(4);

  public void close() throws InterruptedException {
    executor.shutdown();
    executor.awaitTermination(30, TimeUnit.SECONDS);
  }


  public void run() throws InterruptedException, ExecutionException {
    // with rxjava
    // https://medium.com/@bschlining/bridging-completeablefutures-and-rxjava-9dd6f0a9d188
    List<CompletableFuture<String>> futuresList = new ArrayList<>();
    futuresList.add(calculateAsync("Task 1", 1000, null));
    futuresList.add(calculateAsync("Task 2", 100, null));
    futuresList.add(calculateAsync("Task 3", 150, new Exception("Task 3 exception")));
    futuresList.add(calculateAsync("Task 4", 1500, null));

    // generate an observable that emits a value as soon as the future complete
    Observable<String> obs = Observable.create(handler -> {
      futuresList.forEach(f -> {
        f.whenComplete((r, e) -> {
          if (e != null) {
            System.out.println("run - handler exception ");
            handler.onError(e); // unrecoverable error has occurred by terminating the Observable sequence https://github.com/ReactiveX/RxJava/wiki/Error-Handling
          } else {
            handler.onNext(r);
          }
        });
      });
    });
    obs
    .onErrorResumeNext(Observable.empty())
    .subscribe(
        v -> System.out.println("run - future output: " + v),
        e -> System.err.println("run - Exception " + e), () -> System.out.println("All done"));
  }


  private CompletableFuture<String> calculateAsync(String msg, Integer sleep, Exception ex)
      throws InterruptedException {
    String id = "- id: msg_" + msg + "_" + sleep + "_ms";
    CompletableFuture<String> completableFuture = new CompletableFuture<>();
    executor.submit(() -> {
      System.out.println("calculateAsync - Start a future - " + id);
      Thread.sleep(sleep);
      if (ex != null) {
        System.out.println("calculateAsync - Send an exception" + id);
        completableFuture.completeExceptionally(ex);
      } else {
        System.out.println("calculateAsync - Send data" + id);
        completableFuture.complete("calculateAsync return " + id);
      }
      System.out.println("calculateAsync - End a future" + id);
      return null;
    });

    return completableFuture;
  }
}
