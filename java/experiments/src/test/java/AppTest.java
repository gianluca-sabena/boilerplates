import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

//Junit 5
public class AppTest {
    @Test public void testAppHasAGreeting() {
        App classUnderTest = new App();
        assertNotNull("app should have a greeting", classUnderTest.getGreeting());
    }
}

/*
 * This Java source file was generated by the Gradle 'init' task.
 */
// import org.junit.Test;
// import static org.junit.Assert.*;

// import static org.assertj.core.api.Assertions.*;
// public class AppTest {
//     @Test public void testAppHasAGreeting() {
//         App classUnderTest = new App();
//         assertNotNull("app should have a greeting", classUnderTest.getGreeting());
//     }
//     @Test public void shouldBeTrue() {
//         assertThat(true).isTrue();
//     }    
// }