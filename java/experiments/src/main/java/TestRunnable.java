import java.util.concurrent.*;
import java.util.concurrent.TimeUnit;

/**
 * Hello world!
 *
 */
public class TestRunnable 
{
    public static void main( String[] args )
    {
        System.out.println( "Hello World!!!" );
        
        // Thread
        ExecutorService executor = Executors.newFixedThreadPool(4);
        //executor.execute(() -> System.out.println("Zero - Lambda"));
        
        try {
            // based on http://www.baeldung.com/java-completablefuture 
            MyRunnable myRunnable1= new MyRunnable("Runnable-submit-future-1", 3);
            MyRunnable myRunnable2= new MyRunnable("Runnable-submit-future-2", 7);
            Future<?> future1 = executor.submit(myRunnable1);
            Future<?> future2 = executor.submit(myRunnable2);
            future1.get();
            future2.get();
            System.out.println( "Runnable-submit-future-1 and 2 finished!" );
            Thread.sleep(2000);
            Thread myThread = new Thread(new MyRunnable("Runnable-in-thread",5));
            myThread.start();
            Thread.sleep(2000);
            myThread.interrupt(); // Stop thread
            executor.shutdown();
            executor.awaitTermination(5L, TimeUnit.SECONDS);
          } catch (InterruptedException e) {
            System.out.println(e);
          } catch (Exception e) {
            System.out.println(e);
          }
        
        
    }
}
