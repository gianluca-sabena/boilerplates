# Exceed Java SDK Examples

Simple use cases for the Java SDK.

## Settings

If you need to connect with a proxy add host, user and password to settings.xml https://maven.apache.org/settings.html

Copy `settings-example.xml` to `settings.xml` abd **update your ldap username and password**

## Building

```mvn -s settings.xml -Dmaven.repo.local=./tmp -X  compile```

You can also copy over the repositories from `settings.xml`
into your `~/.m2/settings.xml` if you want them to be globally available.


## Running

```mvn exec:java -s settings.xml  -Dmaven.repo.local=./tmp  -Dexec.mainClass=resolver.HelloWorld```
