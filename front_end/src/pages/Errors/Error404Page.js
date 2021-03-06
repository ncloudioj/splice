import React, { Component } from 'react';
import { connect } from 'react-redux';

import { updateDocTitle } from 'actions/App/AppActions';

class Error404Page extends Component {
  componentDidMount() {
    updateDocTitle('Page Not Found');
  }

  render() {
    return (
      <div className="module">
        <div className="module-header">
          Page Not Found
        </div>
        <div className="module-body">
          <div className="row">
            <div className="col-xs-12">
              <p>The page you are looking for does not exist.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

Error404Page.propTypes = {};

// Which props do we want to inject, given the global state?
function select(state) {
  return {
    Account: state.Account,
    App: state.App
  };
}

// Wrap the component to inject dispatch and state into it
export default connect(select)(Error404Page);
