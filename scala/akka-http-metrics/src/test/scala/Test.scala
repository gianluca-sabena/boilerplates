import org.scalatest.{ Matchers, WordSpec }
import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.testkit.ScalatestRouteTest
import akka.http.scaladsl.server._
import Directives._
import boilerplate.akka.http.metrics.Main

class Test extends WordSpec with Matchers with ScalatestRouteTest {

  val route = Main.route

  "The service" should {

    "reurn a echo message for POST request to /api/echi" in {
      Post("/api/echo","HELLO") ~> route ~> check {
        responseAs[String] shouldEqual "HELLO"
      }
    }

    "return a 'PONG!' response for GET requests to /ping" in {
      // tests:
      Get("/api/ping") ~> route ~> check {
        responseAs[String] shouldEqual "PONG!"
      }
    }

    "return a 10 random chars response for GET requests to /api/random/10" in {
      // tests:
      Get("/api/random/10") ~> route ~> check {
        val r = responseAs[String]
        r.length shouldEqual 10
      }
    }

    "leave GET requests to other paths unhandled" in {
      // tests:
      Get("/kermit") ~> route ~> check {
        handled shouldBe false
      }
    }

    "return a MethodNotAllowed error for PUT requests to the root path" in {
      // tests:
      Put() ~> Route.seal(route) ~> check {
        status === StatusCodes.MethodNotAllowed
        responseAs[String] shouldEqual "HTTP method not allowed, supported methods: POST, GET"
      }
    }
  }
}
