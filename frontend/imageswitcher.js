const React = require('react');
const ReactDOM = require('react-dom');

var imageStyle = {
    display: "inline-block",
    margin: "10px",
}
class ImageBox extends React.Component {
    constructor(props) {
            super(props);
            this.state = {currentImage: this.props.imageStart};
    }
    click(image) {
            this.setState({currentImage: image});
    }
    render(){
            const images = this.props.images.map((i)=>
                    React.createElement("div", {style: imageStyle, className: "image", key: i.id},
                            React.createElement("img", {onClick: this.click.bind(this,i), width: "100", src: i.thumbnail}),
                    )
            );
            return React.createElement("div", {className: "gallery"},
            React.createElement("div", {className: "current-image"},
            React.createElement("img",{width:300, height:300, src: this.state.currentImage.image})), images)
    }
}
window.React = React
window.ReactDOM = ReactDOM
window.ImageBox = ImageBox
module.exports = ImageBox