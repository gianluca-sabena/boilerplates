package starter.gradle;

import com.google.inject.Binder;
import com.typesafe.config.Config;
import org.jooby.Env;
import org.jooby.Jooby;
import org.jooby.Router;

public class SimpleModule implements Jooby.Module {
  public void configure(Env env, Config config, Binder binder) {
    
    Router router = env.router();
    /**  Routes from module are considered infrastructure https://github.com/jooby-project/jooby/issues/1002#issuecomment-363073004 */
    router.get("/m1", () -> "I'm a module!");
    
  }

}