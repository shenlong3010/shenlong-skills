Our ingest service throws `NoSuchMethodError: org.apache.commons.lang3.StringUtils.isEmpty(Ljava/lang/CharSequence;)Z` at runtime, but only in the deployed fat jar — locally it builds and tests green. fixtures/pom.xml is our pom; fixtures/tree.txt is the dependency:tree output from the failing environment.

Which version of commons-lang3 is actually on the classpath, who pulled in the conflicting one, and how do I prove which jar the running JVM would load the class from?
