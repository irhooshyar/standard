localStorage.removeItem("last_layout");

class MyGraph {
      constructor(container_id, nodes_data, edges_data, node_features, edge_features, container_width, container_height,
                  default_layout, layout_select_id, is_directed, selected_color,
                  degree_slider_id, weight_slider_id, degree_slider_step, weight_slider_step,
                  nodes_table, edges_table, show_select_neighbour_tag_id, show_hide_image_tag_id,
                  edge_type_name, node_dbl_click_function, edge_dbl_click_function, search_text_box_id, search_text_btn_id)
      {
            this.container_id = container_id;
            this.nodes_data = nodes_data;
            this.edges_data = edges_data;
            this.node_features = node_features;
            this.edge_features = edge_features;
            this.container_width = container_width;
            this.container_height = container_height;
            this.default_layout = default_layout;
            this.layout_select_id = layout_select_id;
            this.is_directed = is_directed;
            this.selected_color = selected_color;
            this.degree_slider_step = degree_slider_step;
            this.weight_slider_step = weight_slider_step;
            this.degree_slider_id = degree_slider_id;
            this.weight_slider_id = weight_slider_id;
            this.nodes_table = nodes_table;
            this.edges_table = edges_table;
            this.show_select_neighbour_tag_id = show_select_neighbour_tag_id
            this.show_hide_image_tag_id = show_hide_image_tag_id;
            this.edge_type_name = edge_type_name;
            this.node_dbl_click_function = node_dbl_click_function;
            this.edge_dbl_click_function = edge_dbl_click_function;
            this.search_text_box_id = search_text_box_id;
            this.search_text_btn_id = search_text_btn_id;

            this.graph_object = null;
            this.data_graph = {nodes: this.nodes_data, edges: this.edges_data};
            this.min_selected_degree = 0;
            this.max_selected_degree = 0;
            this.min_selected_weight = 0;
            this.max_selected_weight = 0;
            this.show_hide_state = "show";

            if (localStorage.getItem("last_layout"))
            {
                this.default_layout = localStorage.getItem("last_layout");
            }
      }

      show()
      {

            // Clear Container; Clear Tables
            document.getElementById(this.container_id).innerHTML = ""

            // Add Default Value to change Layout
            try {
                const query = '[id=' + this.layout_select_id + ']'
                document.querySelectorAll(query).forEach((el) => {
                    let control = el.tomselect;
                    control.setValue(this.default_layout);
                });
            }
            catch (error)
            {
                document.getElementById(this.layout_select_id).value = this.default_layout
            }


            // Copy of Class Object
            const _this = this

            // Directed or UnDirected && cursor
            let edgestyle = {"stroke": "#404040"}

            if (this.edge_dbl_click_function !== "")
            {
                edgestyle["cursor"] = "pointer"
            }
            if (this.is_directed === true)
            {
                edgestyle["endArrow"] = {
                    path: 'M 0,0 L 8,4 L 8,-4 Z',
                    fill: '#404040',
                }
            }


            // Tooltip
            const tooltip = new G6.Tooltip({
                offsetX: 10,
                offsetY: 10,
                itemTypes: ['node', 'edge'],
                getContent: (e) => {
                    const outDiv = document.createElement('div');
                    outDiv.style.width = 'fit-content';
                    let a = e.item.getType()
                    let node_feature_list = ""
                    for (const feature in this.node_features)
                    {
                        node_feature_list += `<p>${this.node_features[feature]}:  ${e.item.getModel()[feature]}</p></div>`
                    }
                    if (a === "node") {
                        outDiv.innerHTML = `<div>
                                                <p>${e.item.getModel().name}</p>
                                                ${node_feature_list}
                                            </div>`;
                    }
                    else if (a === "edge") {
                        let weight_text = ""
                        let edge_feature_list = ""
                        for (const feature in this.edge_features)
                        {
                            edge_feature_list += `<p>${this.edge_features[feature]}:  ${e.item.getModel()[feature]}</p></div>`
                        }
                        if (this.edge_type_name !== "")
                        {
                            weight_text = `<p style="font-weight: bold">${this.edge_type_name}: ${e.item.getModel().weight}</p>`
                        }
                        outDiv.innerHTML = `<div style="direction: rtl">
                                                <p>مبدا: ${e.item.getModel().source_name}</p>
                                                <p>مقصد: ${e.item.getModel().target_name}</p>
                                                ${weight_text}
                                                ${edge_feature_list}
                                            </div>`;
                    }
                    return outDiv;
                }
            });

            // Width and Height
            // const width = this.container_width
            // const height = this.container_height
            const width = document.getElementById(_this.container_id).clientWidth;
            const height = document.getElementById(_this.container_id).clientHeight;

            // Create Graph Object
            this.graph_object = new G6.Graph({
                container: this.container_id,
                width,
                height,
                modes: {
                    default: ['zoom-canvas',
                                'drag-node',
                                'drag-canvas',
                                { type: "brush-select", trigger: 'ctrl' },
                    ],
                },
                plugins: [tooltip],
                layout: {type: this.default_layout, preventOverlap: true},
                animate: true,
                defaultEdge: {
                    style: edgestyle,
                },
                nodeStateStyles: {
                    selected: {
                        stroke: this.selected_color,
                        fill: this.selected_color,
                    },
                    cursor: "pointer"
                },
                defaultNode:{
                    labelCfg: {
                        positions: 'center',
                        style: {
                          cursor: "pointer",
                        }
                    },
                }
            });

            // Render Graph Object
            this.graph_object.data(this.data_graph);
            this.graph_object.render();

            // Canvas Click
            this.graph_object.on('canvas:click', (e) => {
                this.graph_object.getNodes().forEach((node) => {
                    this.graph_object.clearItemStates(node);
                });
                this.graph_object.getEdges().forEach((edge) => {
                    this.graph_object.clearItemStates(edge);
                });
            });

            // NodeSelection Change
            this.graph_object.on('nodeselectchange', e => {
                this.showSelectedData()
            })

            // Node and Edge DblClick Function
            function handleNodeClick(event) {
                const node_data = event.item._cfg.model;
                _this.node_dbl_click_function(node_data)
            }
            this.graph_object.on('node:dblclick', handleNodeClick);

            function handleEdgeClick(event) {
                const edge_data = event.item._cfg.model;
                _this.edge_dbl_click_function(edge_data)
            }
            this.graph_object.on('edge:dblclick', handleEdgeClick);

            // Handle Zoom and Scroll Width
            if (typeof window !== 'undefined') {
                window.onresize = function (event) {
                    const new_width = document.getElementById(_this.container_id).clientWidth;
                    const new_height = document.getElementById(_this.container_id).clientHeight;
                    console.log(new_width, new_height)
                    _this.graph_object.changeSize(new_width, new_height);
                };
            }

            // set MinMax Degree and MinMax Weight
            this.setMinMaxDegree()
            this.setMinMaxWeight()
            this.filterGraphDegreeWeight()
            this.changeLayout()

            // Show Degree Slider and Weight Slider
            if (this.degree_slider_id !== "")
            {
                this.showDegreeSlider()
            }

            if (this.weight_slider_id !== "")
            {
                this.showWeightSlider()
            }

            // Search Select Box
            if (this.search_text_box_id !== "")
            {
                document.getElementById(this.search_text_btn_id).onclick = function () {_this.searchInNodesName()}

                // Add Enter Listener To SearchBox
                let input = document.getElementById(this.search_text_box_id);
                input.addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    document.getElementById(_this.search_text_btn_id).click();
                  }
                });
            }

            // onChange and onClick
            document.getElementById(this.layout_select_id).onchange = function () {_this.changeLayout()}
            document.getElementById(this.show_hide_image_tag_id).onclick = function () {_this.showHideNode()}
            document.getElementById(this.show_select_neighbour_tag_id).onclick = function () {_this.selectNeighbourhood()}

            // Clear Table
            this.showSelectedData()

      }

      selectSingleNode(node_id)
      {
          this.data_graph.nodes.forEach((node) => {
              let item = this.graph_object.findById(node["id"])
              if(node["id"] === node_id)
              {
                    this.graph_object.setItemState(item, 'selected', true);
              }
              else
              {
                    this.graph_object.setItemState(item, 'selected', false);
              }
            })

          this.graph_object.getEdges().forEach((edge) => {
               this.graph_object.setItemState(edge, 'selected', false);
          });

          this.showSelectedData()
      }

      showSelectedData()
      {
            const selected_nodes = this.graph_object.findAllByState('node', 'selected');

            // Add NodesData in Table
            let nodes_data = []
            let id = 1
            for (const node of selected_nodes) {
                const node_object = node._cfg.model
                const node_id = node_object.id
                const node_name = node_object.name


                const _this = this

                const node_tag = $('<a>', {'style': "cursor: pointer; text-align: center; vertical-align: middle"})
                                .text(node_name)
                                .click(function () { _this.node_dbl_click_function(node_object);})

                const degree = this.graph_object.getNodeDegree(node_object.id, 'total');


                const SelectBtn = $('<button>', {'class': "btn modal_btn", "type": "button" })
                                .text("انتخاب");
                const SelectTd = $('<td>').html(SelectBtn).click(function () { _this.selectSingleNode(node_id.toString()); })

                nodes_data.push({ id: id, name: node_tag, degree: degree, node_selection: SelectTd})
                id = id + 1
            }
            $('#'+this.nodes_table).empty();
            $('#'+this.nodes_table).footable({
                "paging": {
                    "enabled": true,
                    strings: {
                        first: '»',
                        prev: '›',
                        next: '‹',
                        last: '«'
                    }
                },
                "filtering": {
                    "enabled": false
                },
                "sorting": {
                    "enabled": true
                },
                "empty": "گره ای انتخاب نشده است",
                "columns": [{
                    "name": "id",
                    "title": "ردیف",
                    "breakpoints": "xs sm",
                    "type": "number",
                    "style": {
                        "width": "5%"
                    }
                }, {
                    "name": "name",
                    "title": "نام گره",
                    "style": {
                        "width": "60%"
                    }
                }, {
                    "name": "degree",
                    "title": "درجه",
                    "style": {
                        "width": "10%"
                    }
                },{
                    "name": "node_selection",
                    "title": "انتخاب",
                    "style": {
                        "width": "10%"
                    }
                }
                ],
                "rows": nodes_data
            });

            // Add EdgesData in Table
            const selected_edges = this.graph_object.findAllByState('edge', 'selected');

            let edges_data = []
            id = 1

            for (const edge of selected_edges) {
                const edge_object = edge._cfg.model
                const src_node_id = edge_object.source
                const src_node_name = edge_object.source_name
                const src_node_object = this.graph_object.findById(src_node_id)._cfg.model
                const target_node_id = edge_object.target
                const target_node_name = edge_object.target_name
                const target_node_object = this.graph_object.findById(target_node_id)._cfg.model
                const weight = edge_object.weight

                const _this = this

                const src_node_tag = $('<a>', {'style': "cursor: pointer; text-align: center; vertical-align: middle"})
                                .text(src_node_name)
                                .click(function () { _this.node_dbl_click_function(src_node_object);})

                const target_node_tag = $('<a>', {'style': "cursor: pointer; text-align: center; vertical-align: middle"})
                                .text(target_node_name)
                                .click(function () { _this.node_dbl_click_function(target_node_object);})

                edges_data.push({ id: id, src_name: src_node_tag, target_name: target_node_tag, weight: weight })
                id = id + 1

            }

            $('#'+this.edges_table).empty();
            $('#'+this.edges_table).footable({
                "paging": {
                    "enabled": true,
                    strings: {
                        first: '»',
                        prev: '›',
                        next: '‹',
                        last: '«'
                    }
                },
                "filtering": {
                    "enabled": false
                },
                "sorting": {
                    "enabled": true
                },
                "empty": "یالی انتخاب نشده است",
                "columns": [{
                    "name": "id",
                    "title": "ردیف",
                    "breakpoints": "xs sm",
                    "type": "number",
                    "style": {
                        "width": "5%"
                    }
                }, {
                    "name": "src_name",
                    "title": "مبدا",
                    "style": {
                        "width": "40%"
                    }
                }, {
                    "name": "target_name",
                    "title": "مقصد",
                    "style": {
                        "width": "40%"
                    }
                }, {
                    "name": "weight",
                    "title": this.edge_type_name,
                    "style": {
                        "width": "15%"
                    }
                },
                ],
                "rows": edges_data
            });

      }

      setMinMaxDegree()
      {
          let min_degree = 1.797693134862315E+308
          let max_degree = 0
          this.data_graph.nodes.forEach((node) => {
                const degree = this.graph_object.getNodeDegree(node["id"], 'total');
                if (degree < min_degree) {
                    min_degree = degree
                }
                if (degree > max_degree) {
                    max_degree = degree
                }
          })

          if (min_degree === 1.797693134862315E+308 || min_degree === 0)
                min_degree = 1

          this.min_selected_degree = min_degree
          this.max_selected_degree = max_degree
      }

      setMinMaxWeight()
      {
          let min_weight = 1.797693134862315E+308
          let max_weight = 0
          this.data_graph.edges.forEach((edge) => {
                const weight = edge["weight"];
                if (weight < min_weight) {
                    min_weight = weight
                }
                if (weight > max_weight) {
                    max_weight = weight
                }
          })

          if (min_weight === 1.797693134862315E+308)
                min_weight = 0

          this.min_selected_weight = min_weight
          this.max_selected_weight = max_weight
      }

      showDegreeSlider()
      {
            document.getElementById(this.degree_slider_id).style.visibility = "visible"

            $('#'+ this.degree_slider_id +' #slider-range').slider({
                range: true,
                min: this.min_selected_degree,
                max: this.max_selected_degree,
                step: this.degree_slider_step,
                values: [this.min_selected_degree, this.max_selected_degree]
            });

            // Move the range wrapper into the generated divs
            $('#'+ this.degree_slider_id +' .ui-slider-range').append($('#'+ this.degree_slider_id +' .range-wrapper'));

            // Apply initial values to the range container
            $('#'+ this.degree_slider_id +' .range').html(
                '<span class="range-value"><sup></sup>' +
                $('#'+ this.degree_slider_id +' #slider-range').slider("values", 0).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") +
                '</span><span class="range-divider"></span><span class="range-value"><sup></sup>' +
                $('#'+ this.degree_slider_id +' #slider-range').slider("values", 1).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") + '</span>');

            // Show the gears on press of the handles
            $('#'+ this.degree_slider_id +' .ui-slider-handle, '+ '#' + this.degree_slider_id +'.ui-slider-range').on('mousedown', function () {
                $('.gear-large').addClass('active');
            });

            var _this = this;

            $('#'+ this.degree_slider_id +' #slider-range').slider({
                slide: function (event, ui) {
                    $('#'+ _this.degree_slider_id +' .range').html(
                        '<span class="range-value"><sup></sup>' +
                        ui.values[0].toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") +
                        '</span><span class="range-divider"></span><span class="range-value"><sup></sup>' +
                        ui.values[1].toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") + '</span>');

                    // Get old value
                    var previousVal = parseInt($(this).data('value'));

                    _this.min_selected_degree = ui.values[0]
                    _this.max_selected_degree = ui.values[1]

                    _this.filterGraphDegreeWeight()

                    // Save new value
                    $(this).data({
                        'value': parseInt(ui.value)
                    });
                }
            });

            $('#'+ this.degree_slider_id +' .ui-slider-handle').parent().css('z-index', 0);

        }

      showWeightSlider()
      {
            document.getElementById(this.weight_slider_id).style.visibility = "visible"
            $('#'+ this.weight_slider_id +' #slider-range').slider({
                range: true,
                min: this.min_selected_weight,
                max: Math.ceil(this.max_selected_weight),
                step: this.weight_slider_step,
                values: [this.min_selected_weight, Math.ceil(this.max_selected_weight)]
            });

            // Move the range wrapper into the generated divs
            $('#'+ this.weight_slider_id +' .ui-slider-range').append($('#'+ this.weight_slider_id +' .range-wrapper'));

            // Apply initial values to the range container
            $('#'+ this.weight_slider_id +' .range').html(
                '<span class="range-value"><sup></sup>' +
                $('#'+ this.weight_slider_id +' #slider-range').slider("values", 0).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") +
                '</span><span class="range-divider"></span><span class="range-value"><sup></sup>' +
                $('#'+ this.weight_slider_id +' #slider-range').slider("values", 1).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") + '</span>');

            // Show the gears on press of the handles
            $('#'+ this.weight_slider_id +' .ui-slider-handle, '+ '#' + this.weight_slider_id +'.ui-slider-range').on('mousedown', function () {
                $('.gear-large').addClass('active');
            });

            var _this = this;
            $('#'+ this.weight_slider_id +' #slider-range').slider({
                slide: function (event, ui) {
                    $('#'+ _this.weight_slider_id +' .range').html(
                        '<span class="range-value"><sup></sup>' +
                        ui.values[0].toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") +
                        '</span><span class="range-divider"></span><span class="range-value"><sup></sup>' +
                        ui.values[1].toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "1,") + '</span>');

                    // Get old value
                    var previousVal = parseInt($(this).data('value'));

                    _this.min_selected_weight = ui.values[0]
                    _this.max_selected_weight = ui.values[1]

                    _this.filterGraphDegreeWeight()

                    // Save new value
                    $(this).data({
                        'value': parseInt(ui.value)
                    });
                }
            });

            $('#'+ this.weight_slider_id +' .ui-slider-handle').parent().css('z-index', 0);

        }

      filterGraphDegreeWeight()
      {
          if (this.graph_object.cfg.states.selected !== undefined)
          {
              this.graph_object.cfg.states.selected.forEach((item) => {
                this.graph_object.setItemState(item, 'selected', false);
              })
          }
          $('#'+this.nodes_table).empty();
          $('#'+this.edges_table).empty();

          this.graph_object.getEdges().forEach((edge) => { edge.show() })
          this.graph_object.getNodes().forEach((node) => { node.show() })

          const min_degree = this.min_selected_degree
          const max_degree = this.max_selected_degree

          const min_weight = this.min_selected_weight
          const max_weight = this.max_selected_weight

          if (this.weight_slider_id !== "")
          {
              this.graph_object.getEdges().forEach((edge) => {
                  const edge_item = edge._cfg.model
                  const edge_weight = edge_item.weight
                  if (edge_weight < min_weight || edge_weight > max_weight) {
                        edge.hide()
                  }
            })
          }

          if (this.degree_slider_id !== "")
          {
              this.graph_object.getNodes().forEach((node) => {
                const node_degree = this.graph_object.getNodeDegree(node._cfg.model.id, 'total');
                if (node_degree < min_degree || node_degree > max_degree) {
                    this.graph_object.findById(node._cfg.model.id).hide();

                    this.graph_object.getEdges().forEach((edge) => {
                        if (edge._cfg.model.source === node._cfg.model.id || edge._cfg.model.target === node._cfg.model.id) {
                            edge.hide()
                        }
                    })
                }
            });
          }
      }

      changeLayout()
      {
          this.graph_object.destroyLayout();
          const layout = document.getElementById(this.layout_select_id).value
          this.graph_object.updateLayout({ type: layout });

          localStorage.setItem("last_layout", layout);
      }

      selectNeighbourhood()
      {
            const selected_node_list = []

            this.graph_object.cfg.states.selected.forEach((item) => {
                const item_cfg = item._cfg
                if (item_cfg.type === "node") {
                    selected_node_list.push(item_cfg.model.id)
                }
            })

            this.graph_object.getEdges().forEach((edge) => {
                if (edge.get('visible') === true) {
                    const source_id = edge._cfg.model.source
                    const target_id = edge._cfg.model.target

                    if (selected_node_list.includes(source_id)) {
                        this.graph_object.setItemState(edge, 'selected', true);
                        this.graph_object.setItemState(this.graph_object.findById(target_id), 'selected', true);
                    }
                    else if (selected_node_list.includes(target_id)) {
                        this.graph_object.setItemState(edge, 'selected', true);
                        this.graph_object.setItemState(this.graph_object.findById(source_id), 'selected', true);
                    }
                }
            });

            this.showSelectedData()

        }

      showHideNode()
      {
            const img_tag_id = this.show_hide_image_tag_id

            if (this.show_hide_state === "show")
            {
                document.getElementById(img_tag_id).src = "../../static/image/show_nodes.png"
                this.show_hide_state = "hide"
                const checked_Nodes = []
                this.graph_object.getEdges().forEach((edge) => {
                    const edge_object = edge._cfg.model
                    const source_object = this.graph_object.findById(edge_object.source)
                    const target_object = this.graph_object.findById(edge_object.target)
                    if (source_object._cfg.states.includes('selected') === false)
                    {
                        source_object.hide()
                    }
                    if (target_object._cfg.states.includes('selected') === false)
                    {
                        target_object.hide()
                    }
                    if (edge._cfg.states.includes('selected') === false)
                    {
                        edge.hide()
                    }
                    checked_Nodes.push(edge_object.source)
                    checked_Nodes.push(edge_object.target)
                });

                this.graph_object.getNodes().forEach((node) => {
                    if(checked_Nodes.includes(node._cfg.model.id) === false &&
                    node._cfg.states.includes('selected') === false)
                    {
                        node.hide()
                    }
                })
            }
            else if (this.show_hide_state === "hide")
            {
                document.getElementById(img_tag_id).src = "../../static/image/hide_nodes.png"
                this.show_hide_state = "show"

                this.filterGraphDegreeWeight()

            }

        }

      textPreprocessing(text)
      {
        text = text.toLowerCase();
        const arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": ""}

        for (const [key, value] of Object.entries(arabic_char)) {
          text = text.replaceAll(key, value)
        }

        while(text.search("  ") !== -1)
        {
            text = text.replaceAll("  ", " ")
        }

        return text
      }

      searchInNodesName()
      {
          const text = document.getElementById(this.search_text_box_id).value

          if (this.graph_object.cfg.states.selected !== undefined)
          {
              this.graph_object.cfg.states.selected.forEach((item) => {
                this.graph_object.setItemState(item, 'selected', false);
              })
          }

          let count = 0
          this.graph_object.getNodes().forEach((node) => {
              const node_object = node._cfg.model
              if(node.get('visible')) {
                  const preprocessed_node_text = this.textPreprocessing(node_object.name)
                  const preprocessed_search_text = this.textPreprocessing(text)
                  if (preprocessed_node_text.startsWith(preprocessed_search_text + " ") === true ||
                      preprocessed_node_text.endsWith(" " + preprocessed_search_text) === true ||
                      preprocessed_node_text.search(" " + preprocessed_search_text + " ") !== -1 ||
                      preprocessed_node_text === preprocessed_search_text) {

                      this.graph_object.setItemState(node, 'selected', true);
                      count += 1
                  }
              }
          })

          this.showSelectedData()

          if (count > 0)
          {
              const message =  count +  " گره یافت شد"
          }
          else
          {
              const message = "گره‌ای یافت نشد"
              Swal.fire({
                  icon: 'warning',
                  html: "<span>"+ message +"</span>",
                  showCloseButton: true,
                  showConfirmButton: false,
                  customClass:{
                      "icon": "styleSwalIcon"
                  }
              })
          }
      }

      getRoot()
      {
          const rootList = []
          this.graph_object.getNodes().forEach((node) => {
              const node_object = node._cfg.model
              const inDegree = this.graph_object.getNodeDegree(node_object.id, 'in');
              const outDegree = this.graph_object.getNodeDegree(node_object.id, 'out');

              if (inDegree === 0 && outDegree > 0)
              {
                  rootList.push(node_object)
              }
          })
          return rootList

      }

      findAllPath(source_node_id, target_node_id, directed)
      {
          const _this = this
          const { findAllPath } = G6.Algorithm;
          const allPath = findAllPath(_this.data_graph, source_node_id, target_node_id, directed);

          let result = []
          for (const path of allPath)
          {
              let local_path = []
              for (const node of path)
              {
                  local_path.push(_this.graph_object.findById(node)._cfg.model)
              }
              result.push(local_path)
          }

          return result
      }

      calculatePathWeight(path_nodes_id)
      {
          let sum_weight = 0
          for (var i = 0; i<path_nodes_id.length-1; i+=1)
          {
              const source_id = path_nodes_id[i]
              const target_id = path_nodes_id[i+1]
              this.graph_object.getEdges().forEach((edge) => {
                  if(edge._cfg.source._cfg.model.id === source_id &&  edge._cfg.target._cfg.model.id === target_id)
                  {
                      sum_weight += parseFloat(edge._cfg.model.weight)
                  }
              })
          }
          return sum_weight
      }

      highlightGraphPath(path_nodes_id)
      {
          this.graph_object.getEdges().forEach((edge) => { this.graph_object.setItemState(edge, 'selected', false); })
          this.graph_object.getNodes().forEach((node) => { this.graph_object.setItemState(node, 'selected', false); })
          for (var i = 0; i< path_nodes_id.length-1 ; i+=1)
          {
              const source_object = this.graph_object.findById(path_nodes_id[i])
              const target_object = this.graph_object.findById(path_nodes_id[i+1])

              this.graph_object.setItemState(source_object, 'selected', true);
              this.graph_object.setItemState(target_object, 'selected', true);

              this.graph_object.getEdges().forEach((edge) => {
                  if(edge._cfg.source._cfg.model.id === path_nodes_id[i] && edge._cfg.target._cfg.model.id === path_nodes_id[i+1])
                  {
                      this.graph_object.setItemState(edge, 'selected', true);
                  }
              })
          }
          this.showSelectedData()
      }

      bfsAlgorithm(source_node_id)
      {
          const result = []
          this.graph_object.getNodes().forEach((node) => {
              var a = this.findAllPath(source_node_id, node._cfg.model.id, true)
              const level = a[0].length

              result.push({node_data: node._cfg.model, level: level})
          })

          return result
      }

}