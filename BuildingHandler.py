import tornado.escape
import tornado.ioloop
import tornado.web


class GetPropertyItemByIdHandler(tornado.web.RequestHandler):
    def get(self, id):
        response = { 'user' : { 'username' : '<string>',
                                'token' : '<string>'
                              },
                     'property_item' : {
                                'type' : 'property',
                                'children' : [
                                            {
                                                'type' : 'building',
                                                'children' : []
                                            },
                                            {
                                                'type' : 'building',
                                                'children' : [{
                                                                'type': 'room',
                                                            'children' : []
                                                            }]
                                            }
                                       ]
                                    }
        }
        self.write(response)

class createPropertyItemHandler(object):
	def post(self, post):
		"""
		user : { username : <string>
				 token : <string>
				}
		property_item : {
			type : property
			children: [
						{
							type : building
							children : {}
						},
						{
							type: building
							children : [
											{
												type: room
												children {}
											}
									   ]
						}
					  ]
		}
		"""

		pass

class CreatePropertyHandler(tornado.web.RequestHandler):
    def get(self):
        # todo: get from db:
        types = ["property","building","floor","room"]
        nesting = {}
        nesting["property"] = ["building"]
        nesting["building"] = ["floor", "room"]

        print(nesting)

        response = """
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
        <div class="panel panel-primary">
        	<div class="panel-heading">Create new collection</div>
        	<div class="panel-body">
        		<ul>
        			<li>
        				<select onchange="createpropertychangelistener(this)">
        					<option value="property">property</option>
        				</select>
        				<input type="text" onchange="createpropertychangelistener(this)">
        			</li>
        		</ul>
        	</div>
        	<div class="panel-footer">footer</div>
        </div>
        <script>

        var nested = {"property" : ["building"],
                      "building" : ["floor","room"],
                      "floor" : ["room"],
                     };

        function createselectoptions(element){
        	options = nested[element];
            result = undefined;
            if(options != undefined){
                result = [];
        	   for(i = 0 ; i < options.length; i++){
                    var tmp = document.createElement("option");
                    tmp.value = options[i];
                    tmp.append(options[i]);
                    result.push(tmp);
        	   }
            }
        	return result;
        }

        function createinnernode(selectoptions){
            var newElement = document.createElement("ul");
            newElement.append(createNode(selectoptions));
            return newElement;
        }

        function createNode(selectoptions){
            var listItem = document.createElement("li");
            var selector = document.createElement("select");
            var inputfield = document.createElement("input");

            inputfield.type = "text";
            inputfield.addEventListener('change', function(){createpropertychangelistener(inputfield)});

            for(var i = 0; i < selectoptions.length; i++){
                selector.append(selectoptions[i]);
            }

            listItem.append(selector);
            listItem.append(inputfield);
            return listItem;
        }

        function createpropertychangelistener(sender){
        	var li = sender.parentElement;
        	var select = li.children[0];
            var lastElementOfParent = li.parentElement.children[li.parentElement.children.length -1];

            // append new parent element:
            
            // create empty node for adding inside at the changed node:
            var options = createselectoptions(select.value);
            if(options != undefined){
                var lastInput = lastElementOfParent.children[1];
                if(lastInput.value != ""){
                    var endNode = createinnernode(options);
                    li.append(endNode);
                }
            }

            // Check if node at end of list is needed:
            var ulElm = li.parentElement;
            var lastElmOfP = ulElm.children[ulElm.children.length -1];
            if(lastElmOfP.children[1].value == ""){
                return;
            }

            // create an empty node at the end of the list:
            // create options:
            var opt = []
            for(var i = 0, len = select.children.length; i < len; i++){
                opt.push(select.children[i].cloneNode(true));
            } 

            var node = createNode(opt);
            li.parentElement.append(node);
        }

        </script>
        """

        self.write(response)



application = tornado.web.Application([
    (r"/getpropertyitembyid/([0-9]+)", GetPropertyItemByIdHandler),
    (r"/createbuilding/", CreatePropertyHandler)
])
 
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()