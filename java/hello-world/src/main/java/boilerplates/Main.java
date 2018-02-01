package boilerplates;

import java.util.concurrent.*;
import java.util.concurrent.TimeUnit;

/**
 * Hello world!
 *
 */
public class Main 
{
    private static final int MESSAGE_LENGTH = 256;
    public static void main( String[] args )
    {
        final long rate = Math.round(1000 / 23424234 * 1000);
        final double th = rate * MESSAGE_LENGTH;
        float th2 =  256.0f / 1024 / 1024 ;
        System.out.printf("Float %f", th2 );
        //System.out.printf(" Rate: %d msg/s - Data: %f byte/s - %f",rate, th, th2 );
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
