package com.boilerplates;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import io.reactivex.Observable;
import io.reactivex.ObservableOnSubscribe;

/**
 * Adapta RxJava wikipedia example
 * https://github.com/ReactiveX/RxJava/wiki/How-To-Use-RxJava#error-handling
 */
 class Data {
  public String name="";
  public String text="";
  public Integer chars  = 0;
  Data(String name, String text, Integer chars){
    this.name = name;
    this.text = text;
    this.chars = chars;
  }
  @Override
  public String toString() {
    return "Name: "+this.name+" - Chars: "+this.chars;
  }
}
public class Wikipedia {

  /**
   * From https://docs.oracle.com/javase/tutorial/networking/urls/readingURL.html
   * @param url
   * @return
   * @throws IOException
   */
  private static String readUrl(String url) throws IOException {
    //System.out.println("--- readUrl");
    URL oracle = new URL("https://en.wikipedia.org/wiki/"+url);
    BufferedReader in = new BufferedReader(new InputStreamReader(oracle.openStream()));
    StringBuilder out = new StringBuilder();
    String inputLine;
    while ((inputLine = in.readLine()) != null) {
      //System.out.println("---:"+inputLine);
      out.append(inputLine);
    }
    in.close();
    return out.toString();
  }

  public static void createObservable(final List<String> pageTitles) throws InterruptedException {
    ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();
    ObservableOnSubscribe<Data> handler = emitter -> {

      Future<Object> future = executor.schedule(() -> {
        try {
          for (String articleName : pageTitles) {
            if (true == emitter.isDisposed()) {
              return null;
            }
            Data d = new Data(articleName, readUrl(articleName), 0);
            emitter.onNext(d);
          }
          if (false == emitter.isDisposed()) {
            emitter.onComplete();
          }
        } catch (Throwable t) {
          if (false == emitter.isDisposed()) {
            emitter.onError(t); // unrecoverable error has occurred by terminating the Observable sequence https://github.com/ReactiveX/RxJava/wiki/Error-Handling
          }
        }
        emitter.onComplete();
        return null;
      }, 1, TimeUnit.SECONDS);

      emitter.setCancellable(() -> future.cancel(false));
    };

    Observable<Data> observable = Observable.create(handler);

    observable.map(data -> {
       data.chars = data.text.length();
       return data;
     }
    ).subscribe(item -> System.out.println(item), error -> error.printStackTrace(),
        () -> System.out.println("Done"));

    Thread.sleep(10000);
    executor.shutdown();
  }
}
// try {
// for (String articleName : pageTitles) {
// if (true == subscriber.isDisposed()) {
// return;
// }
// subscriber.onNext(readUrl(articleName));
// }
// if (false == subscriber.isDisposed()) {
// subscriber.onComplete();
// }
// } catch (Throwable t) {
// if (false == subscriber.isDisposed()) {
// subscriber.onError(t);
// }
// }
