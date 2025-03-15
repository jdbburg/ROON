

export let config = {
    grid: {
        visible: true,
        snapping: true, 
        spacing: 20, // space between grid lines
        major: {
            color: 'hsl(1, 100%, 90%)',
            stroke_width: 1,
            interval: 10
        },
        minor: {
            color: 'hsl(1, 100%, 95%)',
            stroke_width: 1
        }
    },
    node: {
        width: 200,
        height: 100,
        socket: {
            separation: 25,
            radius: 5
        },
        header: {
            height: 40
        }
    },
    link:{
        active: {
            color: 'hsl(1, 100%, 10%)',
            stroke_width: 2
        },
        cut: {
            color: '#ff1100',
            stroke_width: 2
        }
    }
};