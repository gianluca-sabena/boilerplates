package starter.gradle;

import java.util.concurrent.Executors;
import org.jooby.Jooby;

class Database {
  public String fetch(String id) throws InterruptedException {
    Thread.sleep(100);
    return "Data from DB - id: " + id;
  }
}


class RemoteService {
  public String call(String id) throws InterruptedException {
    Thread.sleep(1000);
    return "Data from slow Service - id: " + id;
  }
}
 class CpuIntensive {
  public String run() throws InterruptedException {
    Thread.sleep(5000);
    return "Cpu Intensive Task";
  }
 }


public class ThreadModel extends Jooby {
  {
    executor("db", Executors.newCachedThreadPool());
    executor("remote", Executors.newFixedThreadPool(32));
    executor("intensive", Executors.newSingleThreadExecutor());

    get("/nonblocking", () -> "I'm nonblocking");

    get("/database", deferred("db", req -> {
      Database db = require(Database.class);
      return db.fetch("1");
    }));

    get("/service", deferred("remote", req -> {
      RemoteService rs = require(RemoteService.class);
      return rs.call("1");
    }));

    get("/cpuintensive", deferred("intensive", req -> {
      CpuIntensive ci = require(CpuIntensive.class);
      return ci.run();
    }));
  }

}
