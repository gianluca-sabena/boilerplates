
/**
 * Copyright (C) 2015 Red Hat, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.function.*;
import java.util.concurrent.*;

import io.fabric8.kubernetes.api.model.ObjectMeta;
import io.fabric8.kubernetes.api.model.RootPaths;
import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinition;
import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinitionBuilder;
import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinitionList;
import io.fabric8.kubernetes.client.CustomResourceList;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientException;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.client.dsl.NonNamespaceOperation;
import io.fabric8.kubernetes.client.dsl.Resource;
import io.fabric8.kubernetes.client.internal.SerializationUtils;
import io.fabric8.kubernetes.client.Watch;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.api.model.ReplicationController;
import crds.DoneableDummy;
import crds.Dummy;
import crds.DummyList;
import crds.DummySpec;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Date;
import java.util.List;

public class Crd {

  private static final Logger logger = LoggerFactory.getLogger(Crd.class);

  private static String DUMMY_CRD_GROUP = "demo.fabric8.io";
  private static String DUMMY_CRD_VERSION = "v1";
  private static String DUMMY_CRD_NAME = "dummies." + DUMMY_CRD_GROUP;
  private static String K8S_NAMESPACE = "default";
  private KubernetesClient client;
  private CustomResourceDefinition dummyCRD;
  private Dummy dummyObj;
  private NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> dummyClient;

  private CustomResourceDefinition buildDummyCrd() {
    return new CustomResourceDefinitionBuilder().withApiVersion("apiextensions.k8s.io/v1beta1").withNewMetadata()
        .withName(DUMMY_CRD_NAME).endMetadata().withNewSpec().withGroup(DUMMY_CRD_GROUP).withVersion("v1")
        .withScope("Namespaced").withNewNames().withKind("Dummy").withShortNames("dummy").withPlural("dummies")
        .endNames().endSpec().build();
  }

  private void printDummyCrd() {
    try {
      logger.debug("build CRD " + SerializationUtils.dumpAsYaml(this.dummyCRD));
    } catch (Exception e) {
      logger.error(e.getMessage(), e);
    }
  }

  public Crd(KubernetesClient client) {
    this.client = client;
    this.dummyCRD = buildDummyCrd();
    this.dummyClient = createDummyClient();
    this.dummyObj = buildDummyObj();
    // When you ca say lucky! https://github.com/fabric8io/kubernetes-client/issues/1099#issuecomment-413622028
    io.fabric8.kubernetes.internal.KubernetesDeserializer.registerCustomKind(DUMMY_CRD_GROUP + "/" + DUMMY_CRD_VERSION + "#Dummy", Dummy.class);
    printDummyCrd();
  }

  public void logRootPaths() {
    RootPaths rootPaths = client.rootPaths();
    if (rootPaths != null) {
      List<String> paths = rootPaths.getPaths();
      if (paths != null) {
        System.out.println("Supported API Paths:");
        for (String path : paths) {
          System.out.println("    " + path);
        }
        System.out.println();
      }
    }
  }

  public void deleteDummyCrd() {
    Boolean ret = client.customResourceDefinitions().delete(dummyCRD);
    logger.debug("Delete crd: " + ret);
  }

  public void createDummyCrd() {
    client.customResourceDefinitions().create(dummyCRD);
    logger.debug("Create crd");
  }

  private NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> createDummyClient() {
    // lets create a client for the CRD
    NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> dummyClient = client
        .customResources(dummyCRD, Dummy.class, DummyList.class, DoneableDummy.class).inNamespace(K8S_NAMESPACE);

    return dummyClient;
  }

  private void listDummyObj() {
    // CustomResourceList<Dummy> dummyList = dummyClient.list();
    // List<Dummy> items = dummyList.getItems();
    // System.out.println(" found " + items.size() + " dummies");
    // for (Dummy item : items) {
    // System.out.println(" " + item);
    // }
  }

  private Dummy buildDummyObj() {
    Dummy dummy = new Dummy();
    ObjectMeta metadata = new ObjectMeta();
    metadata.setName("foo");
    dummy.setMetadata(metadata);
    DummySpec dummySpec = new DummySpec();
    Date now = new Date();
    dummySpec.setBar("beer: " + now);
    dummySpec.setFoo("cheese: " + now);
    dummy.setSpec(dummySpec);
    try {
      logger.debug("Dummy crd obj: " + SerializationUtils.dumpAsYaml(dummy));
    } catch (Exception e) {
      logger.error(e.getMessage(), e);
    }
    return dummy;
  }

  public Dummy createDummyObj() {
    Dummy created = dummyClient.createOrReplace(dummyObj);
    logger.info("Upserted " + dummyObj);
    return created;
  }

  public void watchAll() {
    Watch watch = client.replicationControllers().inNamespace(K8S_NAMESPACE).watch(new Watcher<ReplicationController>() {
      @Override
      public void eventReceived(Action action, ReplicationController resource) {
        logger.info("{}: {}", action, resource.getMetadata().getResourceVersion());
      }

      @Override
      public void onClose(KubernetesClientException e) {
        logger.debug("Watcher onClose");
        if (e != null) {
          logger.error(e.getMessage(), e);
        }
      }
    });

  }

  public void watchCrd() {
    logger.info("Watching for changes to Dummies");
    // use global crd version resource instead objCrd
    dummyClient.withResourceVersion(dummyObj.getMetadata().getResourceVersion()).watch(new Watcher<Dummy>() {
      @Override
      public void eventReceived(Action action, Dummy resource) {
        logger.info("==> ACTION watched!");
        // logger.info("==> " + action + " for " + resource);
        // if (resource.getSpec() == null) {
        // logger.error("No Spec for resource " + resource);
        // }
      }

      @Override
      public void onClose(KubernetesClientException cause) {
      }
    });
  }

  public void list() {
    try {
      CustomResourceDefinitionList crds = client.customResourceDefinitions().list();
      List<CustomResourceDefinition> crdsItems = crds.getItems();
      System.out.println("Found " + crdsItems.size() + " CRD(s)");

      for (CustomResourceDefinition crd : crdsItems) {
        ObjectMeta metadata = crd.getMetadata();
        if (metadata != null) {
          String name = metadata.getName();
          System.out.println("    " + name + " => " + metadata.getSelfLink());
          if (DUMMY_CRD_NAME.equals(name)) {
            dummyCRD = crd;
          }
        }
      }
      // if (dummyCRD != null) {
      // System.out.println("Found CRD: " + dummyCRD.getMetadata().getSelfLink());
      // } else {
      // System.out.println("Created CRD " + dummyCRD.getMetadata().getName());
      // }

      // lets create a client for the CRD

    } catch (KubernetesClientException e) {
      logger.error(e.getMessage(), e);
    } catch (Exception e) {
      logger.error(e.getMessage(), e);
    }
  }

}
