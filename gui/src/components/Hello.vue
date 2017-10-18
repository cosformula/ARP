<template>
  <div class="hello">
    <h5>Welcome to ARP studio</h5>
    <d3-network :net-nodes="nodes" :net-links="links" :options="options" style="height:500px;">
    </d3-network>
    <!-- <div id="net"> </div> -->
    <ul>
      <li>
        <q-btn @click.native="start()">refresh</q-btn>
      </li>
      <li v-if="sniffProcess===null">
        <q-btn @click.native="killSniff">stop sniff</q-btn>
      </li>
      <li v-else>
        <q-btn @click.native="sniff">start sniff</q-btn>
      </li>
      <li>
        <q-btn @click.native="scan">scan</q-btn>
      </li>
    </ul>
    <!-- <p></p> -->
  </div>
</template>

<script>
/* eslint-disable */
import D3Network from "vue-d3-network";
// import vis from 'vis'
export default {
  components: {
    D3Network
  },
  name: "hello",
  data() {
    return {
      nodes: [],
      links: [],
      options: {
        force: 4000,
        nodeSize: 30,
        nodeLabels: true,
        fontSize: 20,
        linkWidth: 5
      },
      container: null,
      network: null,
      ARP: {},
      nodeTable: {},
      sniffProcess: null,
      gateway: null
    };
  },
  mounted() {
    this.start();
  },
  methods: {
    clear() {
      this.nodes = [];
      this.edges = [];
      this.nodeTable = {};
    },
    start() {
      this.clear();
      this.getGateway();
    },
    getGateway() {
      console.log("starting get gateway");
      let gateway = spawn("python", ["-u", "../../main.py", "gateway"]);
      gateway.stdout.on("data", data => {
        let msgs = data.toString().split("\r\n");
        for (let msg of msgs) {
          let body = msg.split(" ");
          if (body[0] === "gateway") {
            this.gateway = body[1];
            console.log("gateway set", this.gateway);
            this.scan();
          }
        }
      });
      gateway.on("close", code => {
        console.log(`child process exited with code ${code}`);
        // this.scan();
      });
    },
    addNode: function(node) {
      if (this.nodeTable[node.ip] !== undefined) {
        // this.nodes[this.nodeTable[node.ip]] = node
      } else {
        this.nodes.push(node);
        this.nodeTable[node.ip] = this.nodes.length - 1;
        this.links.push({
          sid: this.nodes[this.nodeTable[this.gateway]].id,
          tid: this.nodes[this.nodes.length - 1].id
        });
      }
    },
    sniff: function() {
      /* eslint-disable no-undef */
      console.log("starting sniffing");
      this.sniffProcess = spawn("python", ["-u", "../../main.py", "sniff"]);
      this.sniffProcess.on("close", code => {
        console.log(`child process exited with code ${code}`);
      });
      this.sniffProcess.stdout.on("data", data => {
        // this.addEdge();
        this.nodes.push({
          id: 1,
          name: "0"
        });
        let i = this.nodes.length;
        console.log(`stdout: ${data}`);
        // console.log(`stdout: ${data}`)
        let msgs = data.toString().split("\r\n");
        for (let msg of msgs) {
          let body = msg.split(" ");
          let type = body[0];
          let src = {
            mac: body[1],
            ip: body[2]
          };
          if (body.length === 6 && this.nodeTable[src.ip] === undefined) {
            this.addNode({
              id: src.ip,
              name: src.ip,
              mac: src.mac,
              ip: src.ip
            });
          }
          var nodeSrc = this.nodes[this.nodeTable[src.ip]];
          let dst = {
            mac: body[4],
            ip: body[5]
          };
          var nodeDst = this.nodes[this.nodeTable[dst.ip]];
          let fun = function(node) {
            return () => {
              node._color = "";
              // if (!node._size <= 30) {
              //   node._size = 30;
              // } else {
              //   node._size -= 10;
              // }
            };
          };
          if (type === "who-has") {
            if (nodeSrc !== undefined) {
              nodeSrc._color = "yellow";
              setTimeout(fun(nodeSrc), 300);
            }
            // nodeSrc._size += 10;

            if (nodeDst !== undefined) {
              nodeDst._color = "red";
              setTimeout(fun(nodeDst), 300);
            }
            // nodeDst._size += 10;
          } else if (type === "is-at") {
            if (nodeSrc !== undefined) {
              nodeSrc._color = "blue";
              setTimeout(fun(nodeSrc), 300);
            }
            // nodeSrc._size += 10;
            if (nodeDst !== undefined) {
              nodeDst._color = "green";
              setTimeout(fun(nodeDst), 300);
            }
            // nodeDst._size += 10;
          }
        }
        this.nodes.splice(i - 1, 1);
      });
    },
    killSniff: function() {
      this.sniffProcess.kill();
      this.sniffProcess = null;
    },
    scan: function() {
      this.clear();
      /* eslint-disable no-undef */
      console.log("starting scan");
      const scan = spawn("python", ["-u", "../../main.py", "scan"]);
      // console.log(scan)
      scan.on("close", code => {
        console.log(`child process exited with code ${code}`);
        if (this.sniffProcess === null) {
          this.sniff();
        }
      });
      scan.stdout.on("data", data => {
        console.log(`stdout: ${data}`);
        let msgs = data.toString().split("\r\n");
        for (let msg of msgs) {
          let body = msg.split(" ");
          let type = body[0];
          if (body.length === 3 && type === "scan") {
            let mac = body[1];
            let ip = body[2];
            this.nodes.push({
              id: ip,
              name: ip,
              mac: mac,
              ip: ip
            });
            this.nodeTable[ip] = this.nodes.length - 1;
          }
        }
        for (let i in this.nodes) {
          this.links.push({
            sid: this.nodes[this.nodeTable[this.gateway]].id,
            tid: this.nodes[i].id
          });
        }
      });
      scan.stderr.on("data", data => {
        console.log(`stderr: ${data}`);
      });
    },
    rnd(start, end) {
      return Math.floor(Math.random() * (end - start) + start);
    },
    addEdge: function() {
      let edge = {
        sid: this.nodes[this.rnd(1, 3)].id,
        tid: this.nodes[this.rnd(1, 3)].id
      };
      this.edges.push(edge);
      // this.network.setData({
      //   nodes: this.nodes,
      //   edges: this.edges
      // });
    },

    whohas: function(src, dst) {},
    isat: function(src, dst) {}
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
@import '~vue-d3-network/dist/vue-d3-network.css';
@import '~variables';

.hello {
  margin-top: 50px;

  a {
    color: #35495E;
  }
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}
</style>
