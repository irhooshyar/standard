var G = new jsnx.Graph();
G.addNodesFrom([
    ["تجارت", {
        color: '#64b5f6',
        count: 10

    }],
    ["الکترونیک", {
        color: 'white',
        count: 10

    }],
    ["توسعه", {
        color: 'white',
        count: 10

    }],
    ["معدنی", {
        color: 'white',
        count: 10
    }],
    ["قانونی", {
        color: 'white',
        count: 10

    }]
]);

G.addEdgesFrom([
    ['تجارت', 'الکترونیک'],
    ['تجارت', 'توسعه'],
    ['تجارت', 'معدنی'],
    ['تجارت', 'قانونی'],

]);

// `jsnx.draw` accept a graph and configuration object
jsnx.draw(G, {
    element: element_id,
    withLabels: true,
    nodeStyle: {
        fill: function(d) {
            return d.data.color || '#AAA'; // any node without color is gray
        },
        stroke: '#64b5f6'
    },
    nodeAttr: {
        r: function(d) { return d.data.count * 3; }
    },
    stickyDrag: true,

});
// node.append("circle")
//     .attr("r", );