# Chronicle queue latency

Test latency of <https://github.com/OpenHFT/Chronicle-Queue>

Based on [ChronicleQueueLatencyDistribution.java](https://github.com/OpenHFT/Chronicle-Queue/blob/master/src/test/java/net/openhft/chronicle/queue/ChronicleQueueLatencyDistribution.java)


## Build and run 

- Build `mvn compile`
- Run `mvn exec:java   -Dexec.mainClass=boilerplates.chronicle_queue_latency.App -DenableAffinity=true`

## Notes

Chronicle is super sensible to dependency versions, use [chronicle-bom](https://search.maven.org/#search%7Cgav%7C1%7Cg%3A%22net.openhft%22%20AND%20a%3A%22chronicle-bom%22) to find correct matches, see [pom.xml](./pom.xml)

...