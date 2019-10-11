export default class BackendApi {
    constructor(envName) {
        if (envName == 'production') {
            this.hostName = 'mysite.com';
        } else {
            this.hostName = '127.0.0.1:8000';
        }
        this.baseHttpApi = 'http://' + this.hostName + '/mobile-api'
    }
    auth(username, password) {
        return fetch(
            this.baseHttpApi + `/login/`, {
                method: 'POST',
                headers: {Accept: "application/json", 'Content-Type': "application/json"},
                body: JSON.stringify({
                    username: username,
                    password: password
                }) 
            }
        ).then(
            response => response.json()
        ).catch(
            error => {console.error(error)}
        ).then(
            response => {
                if (response.token) {
                    this.loggedInToken = response.token;
                    return true;
                }
                return false;
            }
        )
    }
    fetchOrders() {
        return fetch(this.baseHttpApi + `/my-orders/`,{
            method: 'GET',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: "Token " + this.loggedInToken
            }
        }).then(response => response.json())
        .catch(error => { console.error(error) })
    }
    fetchShipmentStatus(id) {
        let url = 'http://' + this.baseHttpApi + `my-orders/${id}/tracker` + `/?token=` + this.loggedInToken;
        return fetch(
            url, {
            method: 'GET',
            headers: {
                Authorization: "Token " + this.loggedInToken
            }
        }).then(
            response => response.text()
        ).catch(
            error => {
                console.error(error);
            }
        )
    }
    openMessageStream(id, onMessageCb) {
        var ws_url = 'ws://' + this.hostName + `ws/customer-service/` + id + `/?token=` + this.loggedInToken;
        this.ws = new WebSocket(ws_url);
        this.ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            onMessageCb(data);
        };
        this.ws.onerror = function(error) {
            console.error("websocket error", error);
        }
        this.ws.onopen = function () {
            this.heartbeatTimer = setInterval(this.sendHeartbeat.bind(this), 10000);
        
        }.bind(this); }
    closeMessageStream() {
        clearInterval(this.heartbeatTimer);
        if (this.ws) {
            this.ws.close();
        }
    }
    sendMessage(message) {
        this.ws.send(JSON.stringify(
            {
                type: 'message',
                message: message
            }
        ));
    }
    sendHeartbeat(){
        this.ws.send(JSON.stringify({
            type: 'heartbeat'
        })
        );
    }
    createAbsUrl(relative_uri) {
        return 'http://' + this.hostName + relative_uri;
    }
    }   
