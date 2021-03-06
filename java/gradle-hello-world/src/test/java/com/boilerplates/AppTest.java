/*
 * This Java source file was generated by the Gradle 'init' task.
 */
// package com.boilerplates;

// import static org.junit.Assert.*;

// import org.junit.Test;

// public class AppTest {
//   @Test
//   public void testAppHasAGreeting() {
//     App classUnderTest = new App();
//     assertNotNull("app should have a greeting", classUnderTest.getGreeting());
//   }
// }
package com.boilerplates;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

//Junit 5
public class AppTest {
    @Test public void testAppHasAGreeting() {
        App classUnderTest = new App();
        assertNotNull("app should have a greeting", classUnderTest.getGreeting());
    }
}