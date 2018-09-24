
//package boilerplates;
import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * This Java source file was generated by the Gradle 'init' task.
 */
public class App {
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public String getGreeting() {
        return "Hello world.";
    }

    public static void main(String[] args) {
        logger.debug("TEST LOG");
        String master = "https://localhost:6443/";
        // if (args.length == 1) {
        //     master = args[0];
        // }
        Config config = new ConfigBuilder().withMasterUrl(master).withNamespace("default").build();
        try {
            KubernetesClient client = new DefaultKubernetesClient(config);
            Crd dummyCrd = new Crd(client);
            dummyCrd.createDummyObj("foo");
            dummyCrd.createDummyObj("bar");
            dummyCrd.listDummyObj();
            //dumyCrd.deleteDummyObj();
            System.in.read();
        } catch (Exception e) {
            logger.error(e.getMessage(), e);
        }
        System.out.println(new App().getGreeting());
        
    }
}
