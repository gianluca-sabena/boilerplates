package com.boilerplates.test;

import java.net.URI;
import java.net.URISyntaxException;

import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.xnio.Options;

import io.undertow.Undertow;
import io.undertow.server.HttpHandler;
import io.undertow.server.HttpServerExchange;
import io.undertow.server.handlers.proxy.LoadBalancingProxyClient;
import io.undertow.server.handlers.proxy.ProxyHandler;
import io.undertow.testutils.DefaultServer;
import io.undertow.testutils.HttpClientUtils;
import io.undertow.testutils.TestHttpClient;
import io.undertow.util.Headers;
import io.undertow.util.StatusCodes;

@RunWith(DefaultServer.class)
public class HandlersTest {

    protected static Undertow server1;
    protected static Logger logger = LoggerFactory.getLogger(HandlersTest.class);

    @BeforeClass
    public static void setup() throws URISyntaxException {
        int port = DefaultServer.getHostPort("default");
        server1 = Undertow.builder().addHttpListener(port + 1, DefaultServer.getHostAddress("default"))
                .setSocketOption(Options.REUSE_ADDRESSES, true).setHandler(new HttpHandler() {
                    @Override
                    public void handleRequest(final HttpServerExchange exchange) throws Exception {
                        logger.info("Backend server");
                        exchange.getResponseHeaders().put(Headers.CONTENT_TYPE, "text/plain");
                        
                        exchange.getResponseSender().send("Backend server Hello World");
                    }
                }).build();
        server1.start();

        LoadBalancingProxyClient loadBalancer;
        loadBalancer = new LoadBalancingProxyClient()
                .addHost(new URI("http", null, DefaultServer.getHostAddress("default"), port + 1, null, null, null))
                .setConnectionsPerThread(20);
        ProxyHandler proxyHandler = ProxyHandler.builder().setProxyClient(loadBalancer).setMaxRequestTime(30000)
                .build();
        DefaultServer.setRootHandler(proxyHandler);
    }



    @Test
    public void failRequestWithoutAuthHeader() throws Throwable {
        final StringBuilder resultString = new StringBuilder();
        TestHttpClient client = new TestHttpClient();
        try {
            HttpGet get = new HttpGet(DefaultServer.getDefaultServerURL());
            HttpResponse result = client.execute(get);
            //Assert.assertEquals(StatusCodes.UNAUTHORIZED, result.getStatusLine().getStatusCode());
            resultString.append(HttpClientUtils.readResponse(result));
        } finally {
            client.getConnectionManager().shutdown();
        }
        Assert.assertTrue(resultString.toString().contains("Backend server Hello World"));
    }

    @Test
    public void proxyRequestWithAuthHeader() throws Throwable {
        final StringBuilder resultString = new StringBuilder();
        TestHttpClient client = new TestHttpClient();
        try {
            HttpGet get = new HttpGet(DefaultServer.getDefaultServerURL());
            get.setHeader("Autorization", "A");
            HttpResponse result = client.execute(get);
            Assert.assertEquals(StatusCodes.OK, result.getStatusLine().getStatusCode());
            resultString.append(HttpClientUtils.readResponse(result));
        } finally {
            client.getConnectionManager().shutdown();
        }
        Assert.assertTrue(resultString.toString().contains("Backend server Hello World"));
    }
    @AfterClass
    public static void teardown() {
        server1.stop();
    }
}