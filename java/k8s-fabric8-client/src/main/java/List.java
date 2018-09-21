// From https://raw.githubusercontent.com/fabric8io/kubernetes-client/v4.0.4/kubernetes-examples/src/main/java/io/fabric8/kubernetes/examples/ListExamples.java


import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class List {

  private static final Logger logger = LoggerFactory.getLogger(List.class);

  public static void list(KubernetesClient client) {

      System.out.println(
        client.namespaces().list()
      );

      System.out.println(
        client.namespaces().withLabel("this", "works").list()
      );

      System.out.println(
        client.pods().withLabel("this", "works").list()
      );

      System.out.println(
        client.pods().inNamespace("test").withLabel("this", "works").list()
      );

      System.out.println(
        client.pods().inNamespace("test").withName("testing").get()
      );

  }

}