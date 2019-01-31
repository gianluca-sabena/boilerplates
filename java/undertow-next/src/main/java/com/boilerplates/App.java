package com.boilerplates;

import java.net.URISyntaxException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class App {

  public static void main(final String[] args) throws URISyntaxException {
    Logger logger = LoggerFactory.getLogger(App.class);
    logger.info("Main started");
    Server server = new Server();
    server.buildAndStartServer();
  }

}