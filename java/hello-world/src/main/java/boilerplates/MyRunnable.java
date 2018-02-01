package boilerplates;

import java.lang.Runnable;

public class MyRunnable implements Runnable {
  String id = "";
  int iteration = 1;

  public MyRunnable(String id, int i) {
    this.id = id;
    this.iteration = i;
  }

  public void run() {
    System.out.println("Start MyRunnable id: "+id);
    while (!Thread.currentThread().isInterrupted()) {
      for (int i = 0; i < iteration; i++) {
        System.out.println("Iteration: "+i+" MyRunnable id: "+id);
        try {
          Thread.sleep(1000);
        } catch (InterruptedException e) {
          // We've been interrupted: no more messages.
          System.out.println("InterruptedException in Thread \n Exception:" + e.toString());
        }
      }
      System.out.println("End MyRunnable id: "+id);
      return; // made thread to end
    }
  }
}