
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

import io.fabric8.kubernetes.api.model.HasMetadata;
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
  private NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> dummyClient;

  public Crd(KubernetesClient client) {
    // When you can say lucky!
    // https://github.com/fabric8io/kubernetes-client/issues/1099#issuecomment-413622028
    // and https://groups.google.com/forum/#!topic/fabric8/Q5_aSYyaAtA
    io.fabric8.kubernetes.internal.KubernetesDeserializer
        .registerCustomKind(DUMMY_CRD_GROUP + "/" + DUMMY_CRD_VERSION + "#Dummy", Dummy.class);
    this.client = client;
    // build CRD
    this.dummyCRD = buildDummyCrd();
    dumpYaml(dummyCRD);
    this.dummyClient = createDummyClient();
    // start watchind this crd for changes
    // deleteDummyCrd();
    if (findDummyCrd() == false)
      createDummyCrd();
    this.watchCrd();
  }

  private CustomResourceDefinition buildDummyCrd() {
    return new CustomResourceDefinitionBuilder().withApiVersion("apiextensions.k8s.io/v1beta1").withNewMetadata()
        .withName(DUMMY_CRD_NAME).endMetadata().withNewSpec().withGroup(DUMMY_CRD_GROUP).withVersion(DUMMY_CRD_VERSION)
        .withScope("Namespaced").withNewNames().withKind("Dummy").withShortNames("dummy").withPlural("dummies")
        .endNames().endSpec().build();
  }

  private static void dumpYaml(HasMetadata obj) {
    try {
      logger.debug("Dump obj: '" + obj.getMetadata().getName() + "' yaml: " + SerializationUtils.dumpAsYaml(obj));
    } catch (Exception e) {
      logger.error(e.getMessage(), e);
    }
  }

  private void watchCrd() {
    logger.info("Watching for changes to Dummies");
    // use global crd version resource instead objCrd
    dummyClient.withResourceVersion(dummyCRD.getMetadata().getResourceVersion()).watch(new Watcher<Dummy>() {
      @Override
      public void eventReceived(Action action, Dummy resource) {
        logger.info("WATCH: '" + action + "' for: " + resource);
        if (resource.getSpec() == null) {
          logger.error("No Spec for resource " + resource);
        }
      }

      @Override
      public void onClose(KubernetesClientException cause) {
      }
    });
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

  private void deleteDummyCrd() {
    Boolean ret = client.customResourceDefinitions().delete(dummyCRD);
    logger.debug("Delete crd: " + ret);
  }

  private void createDummyCrd() {
    CustomResourceDefinition crd = client.customResourceDefinitions().create(dummyCRD);
    logger.debug("Create crd: " + crd);
  }

  private NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> createDummyClient() {
    // lets create a client for the CRD
    NonNamespaceOperation<Dummy, DummyList, DoneableDummy, Resource<Dummy, DoneableDummy>> dummyClient = client
        .customResources(dummyCRD, Dummy.class, DummyList.class, DoneableDummy.class).inNamespace(K8S_NAMESPACE);

    return dummyClient;
  }

  public void listDummyObj() {
    CustomResourceList<Dummy> dummyList = dummyClient.list();
    List<Dummy> items = dummyList.getItems();
    logger.info("Found " + items.size() + " dummy Object(s)");
    for (Dummy item : items) {
      logger.info("Dummy Object: " + item);
    }
  }
  public void deleteDummyObj() {
    CustomResourceList<Dummy> dummyList = dummyClient.list();
    List<Dummy> items = dummyList.getItems();
    dummyClient.delete(items);


  }


  private Dummy buildDummyObj(String name) {
    Dummy dummy = new Dummy();
    ObjectMeta metadata = new ObjectMeta();
    metadata.setName(name);
    dummy.setMetadata(metadata);
    dummy.setApiVersion(DUMMY_CRD_VERSION);
    DummySpec dummySpec = new DummySpec();
    Date now = new Date();
    dummySpec.setBar("beer: " + now);
    dummySpec.setFoo("cheese: " + now);
    dummy.setSpec(dummySpec);
    return dummy;
  }

  public Dummy createDummyObj(String name) {
    Dummy dummyObj = buildDummyObj(name);
    dumpYaml(dummyObj);
    Dummy created = dummyClient.createOrReplace(dummyObj);
    logger.info("Create Dummy obj: " + created);
    return created;
  }

  public Boolean deleteDummyObj(List<Dummy> items) {
    return dummyClient.delete(items);
  }

  private boolean findDummyCrd() {
    boolean ret = false;
    try {
      CustomResourceDefinitionList crds = client.customResourceDefinitions().list();
      List<CustomResourceDefinition> crdsItems = crds.getItems();
      logger.debug("Found " + crdsItems.size() + " CRD(s)");

      for (CustomResourceDefinition crd : crdsItems) {
        ObjectMeta metadata = crd.getMetadata();
        if (metadata != null) {
          String name = metadata.getName();
          logger.debug("Found CRD with name: '" + name + "' => " + metadata.getSelfLink());
          if (DUMMY_CRD_NAME.equals(name)) {
            logger.info("CRD already present!");
            dummyCRD = crd;
            ret = true;
          }
        }
      }
    } catch (KubernetesClientException e) {
      logger.error(e.getMessage(), e);
    } catch (Exception e) {
      logger.error(e.getMessage(), e);
    }
    return ret;
  }

}
