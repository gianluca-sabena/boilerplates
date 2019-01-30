package com.boilerplates;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import io.reactivex.*;
import io.reactivex.schedulers.*;

public class RxExamples {
  public static void helloWorld() {
    System.out.println("- Flowable with one element");
    Flowable.just("Hello world").subscribe(System.out::println);
  }

  /**
   * from https://github.com/ReactiveX/RxJava/wiki/Creating-Observables#from
   */
  public static void observableFromList() {
    System.out.println("- observableFromList()");
    ArrayList<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8));

    Observable<Integer> observable = Observable.fromIterable(list);

    observable.subscribe(item -> System.out.print(item+", "), error -> error.printStackTrace(),
        () -> System.out.println("Done"));

  }

  /**
   * Create an observable https://github.com/ReactiveX/RxJava/wiki/Creating-Observables#create
   * 
   * @throws InterruptedException
   */
  public void createObservable() throws InterruptedException {
    System.out.println("- createObservable()");
    ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();
    ObservableOnSubscribe<String> handler = emitter -> {

      Future<Object> future = executor.schedule(() -> {
        emitter.onNext("Hello");
        emitter.onNext("World");
        emitter.onComplete();
        return null;
      }, 1, TimeUnit.SECONDS);

      emitter.setCancellable(() -> future.cancel(false));
    };

    Observable<String> observable = Observable.create(handler);

    observable.subscribe(item -> System.out.println(item), error -> error.printStackTrace(),
        () -> System.out.println("Done"));

    executor.shutdown();
    executor.awaitTermination(30, TimeUnit.SECONDS);
  }

  public static void concurrency() {
    /**
     * Map is not parallel
     */
    System.out.println("- concurrency() map is not parallel");
    long start = System.currentTimeMillis();
    Flowable.range(1, 10).observeOn(Schedulers.computation()).map(v -> v * v)
    .blockingSubscribe((s) -> System.out.print(s+", "));
    System.out.println("Finished concurrency in: " + (System.currentTimeMillis() - start) + "ms");
  }
  
  public static void parallel() {
    /**
     * now it is parallel because it use subscribeOn see also Flowable.range(1, 10).parallel()
     */
    System.out.println("- concurrency() with subscribeOn is now parallel");
    long start = System.currentTimeMillis();
    Flowable.range(1, 10)
        .flatMap(v -> Flowable.just(v).subscribeOn(Schedulers.computation()).map(w -> w * w))
        .blockingSubscribe((s) -> System.out.print(s+", "));
    System.out.println("Finished parallel in: " + (System.currentTimeMillis() - start) + "ms");
  }

 

}
