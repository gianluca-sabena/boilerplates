import React from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import AjaxCall from "./Ajax";

function BasicExample() {
  return (
    <Router>
      <div>
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
          <a className="navbar-brand" href="/">Navbar</a>
          <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav mr-auto">
              <li className="nav-item active">
                {/* <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a> */}
                <Link className="nav-link"  to="/">Home</Link>
              </li>
              <li className="nav-item">
                {/* <a class="nav-link" href="#">Link</a> */}
                <Link className="nav-link" to="/about">About</Link>
              </li>
              <li className="nav-item">
                {/* <a class="nav-link" href="#">Link</a> */}
                <Link className="nav-link" to="/ajax">Ajax</Link>
              </li>
            </ul>
          </div>
        </nav>
        <Route exact path="/" component={Home} />
        <Route path="/about" component={About} />
        <Route path="/ajax" component={AjaxCall} />
      </div>
    </Router>
  );
}

function Home() {
  return (
    <div>
      <h2>Home</h2>
      <p><Link to="/ajax">Test AJAX call</Link></p>
    </div>
  );
}

function About() {
  return (
    <div>
      <h2>About</h2>
    </div>
  );
}



export default BasicExample;