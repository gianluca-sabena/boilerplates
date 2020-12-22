import React from 'react';

class AjaxCall extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    fetch("/uuid")
      .then(response => response.text())
      .then(
        (response) => {
          console.log(response)
          this.setState({
            isLoaded: true,
            items: response
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, items } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <div>
          <h2>Ajax</h2>
          <code>Message from api GET '/api/example': {items}</code>
        </div>
      );
    }
  }
}

export default AjaxCall;