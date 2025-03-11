
import {config} from './CONF'

const hueOverrides = {
  "str": 72,
  "string" : 72,
  "number" : 330
}

export function socketColorForType(type, saturation = 60, lightness = 50) {
    // Simple hash
    let hash = 0;
    for (let i = 0; i < type.length; i++) {
      hash = type.charCodeAt(i) + ((hash << 5) - hash);
      // no need for bitwise & here in JS, but you can do hash |= 0 to keep 32-bit
    }

    // Convert the hash to a hue from 0..359
    let hue = Math.abs(hash) % 360;
    if (type in hueOverrides)
        hue = hueOverrides[type]

    // Return an HSL color with a fixed saturation & lightness
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  }


export function socketPosition( socketFlow: string, index: number ) {
    if (socketFlow == "input"){
        return { x: 0, y: config.node.header.height + index * config.node.socket.separation }
    }  

    return { x: config.node.width, y:config.node.header.height + index * config.node.socket.separation }
}