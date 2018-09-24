# K8S operator in Java

Develop a k8s crd resource and an operator to manage it.

Api <http://www.javadoc.io/doc/io.fabric8/kubernetes-client/4.0.5>

## Build

Install gradle

Build `./gradlew build`
Run `./gradlew run`

Interact from kubectl

- Edit crd object file in [dummyObj.yaml](./util/dummyObj.yaml)
- Create crd obj `kubectl -f create ./util/dummyObj.yaml`
- Delete crd obj `kubectl -f delete ./util/dummyObj.yaml`

## Todo

## Credits

Code derives from Fabric8 k8s client examples <https://github.com/fabric8io/kubernetes-client/tree/master/kubernetes-examples>

## Issues

error on custom watch event serialization

- <https://groups.google.com/forum/#!topic/fabric8/Q5_aSYyaAtA>
- <https://github.com/fabric8io/kubernetes-client/issues/1099#issuecomment-413622028>