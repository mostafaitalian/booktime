import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import LoginView from './src/components/LoginView';
import BackendApi from './src/backend';
export default class App extends React.Component {
  constructor (props) {
    super(props);
    this.backendApi = new BackendApi();
    this.state = {
      loggedIn: false
      };
    }
  render () {

        return (
          <LoginView
              backendApi={this.backendApi}
              setLoggedIn={() => this.setState({loggedIn: true })} />
  );
  }
  }