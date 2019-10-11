import React, { Component } from 'react'
import { Text, View, TextInput, StyleSheet, TouchableHighlight } from 'react-native'
import BackendApi from "../backend"
const styles = StyleSheet.create(
    {
        container: {
            flex: 1,
            justifyContent: "center",
            alignItems: "center"
        },
        welcome: {
            fontSize: 20,
            margin: 10,
            textAlign: "center"
        },
        instructions: {
            fontSize: 17,
            color: 'red',
            marginBottom: 10, 
        },
        input: {
            width: 60,
            height: 40,
            marginBottom: 10,
            fontSize: 17
        }
    }
)

export default class LoginView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            username: "",
            password: ""
        };
        this.handleSubmitLogin = this.handleSubmitLogin.bind(this);
    }
    handleSubmitLogin() {
        if (this.state.username && this.state.password) {
            return new BackendApi('development').auth(this.state.username, this.state.password)
            .then(Loggedin => {
                if (Loggedin) {
                    this.props.setLoggedIn();
                } else {
                    this.setState({
                        username: '',
                        password: ''
                    });
                    alert('you are unable to login');
                }
            });
        }
    }

    render () {
        return (
            <View className="container" style={styles.container}>
                <Text style={styles.welcome}>
                    Welcome
                </Text>
                <Text style={styles.instructions}>
                    login in beow to see ur orders
                </Text>
                <TextInput style={styles.input} placeholder="UserName" value={this.state.username}
                onChangeText={text => { this.setState({username: text})}} />
                <TextInput placeholder="Password" value={this.state.password}
                onChangeText={text => { this.setState({password: text})}} />
                <TouchableHighlight onPress={this.handleSubmitLogin}>
                    <Text>Submit</Text>
                </TouchableHighlight>                
            </View>
        );
    }



}