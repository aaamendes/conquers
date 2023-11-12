from pathlib import Path

class Constants:
    VERSION = "conquers v0.1"
    CHOME = "~/.conquers/"
    CHOME_ABS_PATH = None
    DEFAULT_CONFIG = "config.yaml"
    SOCKET_FILE = "/tmp/conquers.socket"
    """
    UNIX socket for IPC.
    """
    BUFF_SIZE = 1024
    """
    Buffer size for reading from
    :py:class:`~constants.Constants.SOCKET_FILE`.
    """
    HTML_TOP = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <!--<link rel="stylesheet" href="css/main.css">-->
    <title>conquers report</title>
<style>
* { 
  box-sizing: border-box;
}

html,body {
  font-family: Lato,proxima-nova,Helvetica Neue,Arial,sans-serif;
  background: #fcfcfc;
  color: #404040;
  padding: 0;
  margin: 0;
  font-size: 14px;
}

ul {
  list-style: none;
  padding: 0;
}

h1,h2,h3 {
  font-family: sans-serif;
  letter-spacing: .1rem;
  color: #404040;
}
hr {
  display: block;
  height: 1px;
  border: 0;
  border-top-width: 0px;
  border-top-style: none;
  border-top-color: currentcolor;
  border-top: 1px solid #e1e4e5;
  margin: 24px 0 55px 0;
  padding: 0;
}

a {
  text-decoration: none;
  color: #bbb;
  font-size: 1rem;
}

.wrapper {
  position: relative;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.nav-stuff {
  background: #2980b9;
  padding: 1rem;
  display: flex;
  height: 267px;
  justify-content: space-between;
  flex-direction: column;
}
.footer {
  background: #343131 !important;
  height: 144px;
}
ul.links li {
  display: flex;
  justify-content: row;
  align-items: center;
  height: 34px;
}
ul.links li span {
  color: #fcfcfc;
  margin-left: 21px;
}
.nav-stuff span.title {
  text-align: center;
  color: #fcfcfc;
  font-weight: bold;
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-box {
  position: relative;
  height: 2rem;
  color: #333;
  display: flex;
  align-items: center;
  margin-left: 2rem;
}
.search-box::before {
  content: "🔎";
  position: absolute;
  height: 2rem;
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  margin-left: 1rem;
  z-index: 2;
}
.search-box input {
  position: relative;
  width: 15rem;
  padding-left: 2rem;
  z-index: 1;
  padding: 0.5rem 0.5rem 0.5rem 3rem;
  border-radius: 2rem;
  border: 1px solid #2472a4;
  background: #fcfcfc;
  color: #aaa;
  font-style: italic;
  transition: width .3s;
}
.search-box input:focus,
.search-box input:active {
  outline: none;
}

.main {
  display: flex;
  flex-direction: row
}

.hosts-nav-wrapper {
  background: #fcfcfc;
  height: calc(100vh - 5rem + 70px);
  padding: 0;
}
.host-content-wrapper {
  padding: 0 1rem;
  width: 100%;
  background: #fcfcfc;
  height: calc(100vh - 5rem + 70px);
}
.hosts-nav-content {
  width: 300px;
  white-space: nowrap;
  background: #343131;
}

.hosts-nav-content, .host-content {
  overflow: auto;
  height: calc(100vh - 5rem + 70px);
  transition: width .3s;
}
.host-content {
  padding: 2rem;
  background: #fcfcfc;
}

label {
  color: #55a5d9;
  font-weight: bold;
}

label.alone {
  display: block;
  padding: .8rem;
  font-weight: bold;
  color: #55a5d9;
}

ul.hosts-nav-entries, ul.hosts-nav-sub {
  width: 100%;
  list-style: none;
  margin: 0;
  padding: 0;
}
ul.hosts-nav-entries li {
  width: 100%;
  margin: 0;
  padding: .8rem;
  cursor: pointer;
  color: #d9d9d9;
  background: #4e4a4a;
}
ul.hosts-nav-entries li:hover {
  background: #555050;
}

.sub-li {
  padding: 0 !important;
}
.sub-li:hover {
  background: #fcfcfc;
}

ul.hosts-nav-sub li.sub-li-item {
  background: #e3e3e3;
  padding: .5rem;
  padding-left: 2rem;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #404040;
  border-right: 1px solid #c9c9c9;
}
ul.hosts-nav-sub li:hover, ul.hosts-nav-sub li:focus, ul.hosts-nav-sub li:active {
  background: #d6d6d6;
}

.sub-li-item-active {
  background: #fcfcfc !important;
  border-right: 1px solid #fcfcfc !important;
  border-top: 1px solid #c9c9c9;
  border-bottom: 1px solid #c9c9c9;
}

span.info-box {
  color: #999;
  font-style: italic;
  background: #fcfcfc;
  padding: 1rem;
  border-radius: 1rem;
}
span.info-box::before {
  content: "ℹ️ ";
  font-style: normal;
}

table {
	border-collapse: collapse;
  width: 100%;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  color: #555;
  margin-bottom: 21px;
}
table thead {
  cursor: pointer;
}
table thead tr {
  background: #fcfcfc;
  color: #555;
  text-align: left;
}

table th, table td {
	padding: 12px 15px;
}
td {
}
td:first-child {
  font-style: normal;
}

table tbody tr {
    border-bottom: 1px solid #ececec;
}

table tbody td {
  font-family: monospace;
}

table tbody tr:nth-of-type(even) {
  background: #fcfcfc;
}
table tbody tr:nth-of-type(odd) {
  background: #f7f7f7;
}

table tbody tr:last-of-type {
    border-bottom: 2px solid #d5d5d5;
}

.error-red {
  /*color: #671c1c;*/
  color: red !important;
}
.ok-green {
  color: #457045;
}

.github::before {
  content: '';
  border-bottom: 0;
  display: inline-block;
  vertical-align: middle;
  margin-right: 21px;
  width: 26px;
  height: 26px;
  background: url("data:image/png;base64,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");
  background-repeat: no-repeat;
  background-size: contain;
}
</style>
  </head>
  <body>
    <div class="wrapper">
      <div class="main">
        <div class="hosts-nav-wrapper">
          <div class="hosts-nav-content">

            <div class="nav-stuff">
              <span class="title">conquers
                report</span>
              <div class="logo">
                <img src="https://cdn.amendes.me/conquers/logo.svg" width=144 alt="logo">
              </div>
              <div class="search-box">
                <input id="search-input" placeholder="filter hosts">
              </div>
            </div>

            <label class="alone">🏘️ GROUPS:</label>
            <ul class="hosts-nav-entries">
'''
    """
    Top part of the html page that can be generated as a report.
    Yes, it's ugly but it works.
    """

    HTML_BOTTOM = '''
            </ul>

            <div class="nav-stuff footer">
            <label>🔗 LINKS:</label>
              <ul class="links">
                <li>
                  <a 
                  href="https://github.com/medecaj/conquers"
                  class="github"
                  target="_blank">
                    conquers
                  </a>
                </li>
                <li>
                  <a 
                  href="https://github.com/medecaj/conquers-report"
                  class="github"
                  target="_blank">
                    conquers-report
                  </a>
                </li>
              </ul>
            </div>

          </div>
        </div>
        <div class="host-content-wrapper">
          <div class="host-content" id="host-content">
            <span class="info-box">
              Click a host on the left to see its report.
            </span>
          </div>
        </div>
      </div>

    </div>
    <!--<script src="js/main.js"></script>-->
    <script>
(() => {
  'use strict';

  class FilterHosts {
    constructor() {
      this.list = document.getElementsByClassName("sub-li-item");
      this.search_input = document.getElementById("search-input");
      this.addEvent();
    }
    addEvent() {
      this.search_input.addEventListener("keyup", (e) => {
        let value = this.search_input.value;
        for(let i = 0; i < this.list.length; i++) {
          if(this.list[i].textContent.toLowerCase().includes(
            value.toLowerCase()
            )
          ) {
            this.list[i].style.display = "block";
          }
          else {
            this.list[i].style.display = "none";
          }
        }
      });
    }
  }

  class Expander {
    constructor(elem, target, cssVisibleAttribute, useOpacityActive=false) {
      this.elem = elem;
      this.target = target
      this.open = true;
      this.cssVisibleAttribute = cssVisibleAttribute;
      this.add_click_event();
      this.useOpacityActive = useOpacityActive;
    }

    add_click_event() {
      this.elem.addEventListener("click", (e) => {
        if(this.useOpacityActive)
          this.elem.style.opacity = (this.open) ? "0.5" : "1";
        this.target.style.display = (this.open) ? "none" : this.cssVisibleAttribute;
        this.open = !this.open;
      });
    }
  }
  /*** class Expander END *********************************/

  class HTMLBuilder {
    constructor(elem) {
      this.clicked_node = elem;
      this.obj = {};
      this.group = "";
      this.host_obj = {};
      this.host = "";
      this.error = "";
      this.html = "";
      this.json_string = "";
      this.contentNode = this.gid("host-content");
      this.check_error_set_color();
      this.add_click_event(elem);
      this.subListItemCssClass = "sub-li-item";
      this.activeListCssClass = "sub-li-item-active";
    }
    /*** constructor END ***************/

    /*
     * Check for error length in dataset-json
     * and sets hostname green for ok or red
     * if errors occured.
     */
    check_error_set_color() {
      this.json_string = this.clicked_node.dataset.json;

      /*
       * Get JSON object from dataset.
       */
      try {
        this.obj = JSON.parse(this.json_string)
      }
      catch(e) {
        let error = "[ERROR] No JSON data or erroneous data. This is a bug.";
        this.error = this.ce("p");
        this.error.textContent = error;
        this.error.classList.add("error-red");
        this.clicked_node.classList.add("error-red");
        return;
      }

      // Get first key with is the group name.
      for(let g in this.obj) {
        this.group = g;
        break;
      }

      // Get the host name and set object.
      for(let h in this.obj[this.group][0]) {
        this.host = h;
        this.host_obj = this.obj[this.group][0][h]
        break;
      }

      if(this.host_obj["errors"].length > 0)
        this.clicked_node.classList.add("error-red");
      else 
        this.clicked_node.classList.add("ok-green");
    }
    /*** check_error_set_color END *****/

    /*
     * shorteners
     */
    ce(elem) {
      return document.createElement(elem);
    }
    gid(elem) {
      return document.getElementById(elem);
    }
    gc(elem) {
      return document.getElementsByClassName(elem);
    }
    gt(elem) {
      return document.getElementsByTagName(elem);
    }
    /*** shorteners END ****************/

    set_active(elem) {
      let all_items = document.getElementsByClassName(this.subListItemCssClass);
      for(let i = 0; i< all_items.length; i++) {
        all_items[i].classList.remove(this.activeListCssClass);
      }

      elem.classList.add(this.activeListCssClass);
    }
    /*
     * Add click event for host item:
     *  * sets clicked elem avtive
     *  * builds html
     *  * shows html
     *  * makes tables expandable using class Expander
     */
    add_click_event(elem) {
      elem.addEventListener("click", (e) => {
        this.set_active(elem);
        this.buildHTML(elem);
        this.show_html().then(
          (resp) => {
            setTimeout(() => {
              let heads = document.getElementsByTagName("thead");

              for(let i = 0; i < heads.length; i++) {
                let target = heads[i].parentNode.getElementsByTagName("tbody")[0];
                let expander = new Expander(
                  heads[i],
                  target,
                  "table-row-group",
                  true
                );
              }
            }, 100);
          }
        )
      });
    }
    /*** add_click_event END ***********/

    create_commands_table(type) {
      const t = {
        table: { 
          node: this.ce("table")
        },
        thead: {
          tr: this.ce("tr"),
          node: this.ce("thead")
        },
        tbody: {
          node: this.ce("tbody")
        },
      };

      t.thead.node.appendChild(t.thead.tr);

      [
        type,
        "output"
      ].map((text, i) => {
        let th = this.ce("th");
        th.textContent = text;
        t.thead.tr.appendChild(th);
      });

      t.table.node.append(
        t.thead.node,
        t.tbody.node,
      );

      if(typeof(this.host_obj["config"]["settings"][type]) === "object") {
        /*
         * One array can be larger than the other.
         * Find the larger one and use its length in the for loop.
         */
        const len = (
          this.host_obj["config"]["settings"][type].length >
            this.host_obj["output"][type].length
        ) ? this.host_obj["config"]["settings"][type].length :
              this.host_obj["output"][type].length;

        for(let i = 0; i < len; i++) {
          let tr = this.ce("tr");
          let td1 = this.ce("td");
          let td2 = this.ce("td");

          td1.textContent = (
            typeof(this.host_obj["config"]["settings"][type][i]) === "undefined"
          ) ? "" : this.host_obj["config"]["settings"][type][i];
          td2.textContent = (
            typeof(this.host_obj["output"][type][i]) === "undefined"
          ) ? "" : this.host_obj["output"][type][i];

          tr.append(td1, td2);

          t.tbody.node.appendChild(tr);
        }
      }

      return t;
    }
    /*** create_commands_table END *****/

    buildHTML(elem) {
      // No dataset -> return
      // This should not happen.
      if(Object.keys(this.obj).length === 0)
        return;

      const body = this.ce("div");

      const heading = this.ce("h2");
      heading.textContent = `Host ${this.host}`;

      const hr = this.ce("hr");

      body.appendChild(heading);
      body.appendChild(hr);

      const div = this.ce("div");

      /*
       * Create summary table.
       */
      const summary = {
        table: {
          node: this.ce("table")
        },
        tbody: {
          node: this.ce("tbody"),
          tr: this.ce("tr"),
          group: {
            node: this.ce("td")
          },
          host: {
            node: this.ce("td"),
          },
          user: {
            node: this.ce("td"),
          },
          message: {
            node: this.ce("td")
          },
          rc: {
            node: this.ce("td")
          },
          errors: {
            node: this.ce("td")
          }

        },
        thead: {
          node: this.ce("thead"),
          tr: {
            node: this.ce("tr")
          },
          th: {
            group: {
              node: this.ce("th")
            },
            host: {
              node: this.ce("th")
            },
            user: {
              node: this.ce("th")
            },
            message: {
              node: this.ce("th")
            },
            rc: {
              node: this.ce("th")
            },
            errors: {
              node: this.ce("th")
            }
          }
        }
      };

      summary.table.node.append(
        summary.thead.node,
        summary.tbody.node
      );
      summary.thead.node.append(
        summary.thead.tr.node
      );
      summary.thead.tr.node.append(
        summary.thead.th.group.node,
        summary.thead.th.host.node,
        summary.thead.th.user.node,
        summary.thead.th.message.node,
        summary.thead.th.rc.node,
        summary.thead.th.errors.node,
      );
      [
        summary.thead.th.group.node,
        summary.thead.th.host.node,
        summary.thead.th.user.node,
        summary.thead.th.message.node,
        summary.thead.th.rc.node,
        summary.thead.th.errors.node,
      ].map((node, i) => { 
        node.setAttribute("scope", "col");

        switch(i) {
          case 0:
            node.textContent = "Group";
            break;
          case 1:
            node.textContent = "Host";
            break;
          case 2:
            node.textContent = "User";
            break;
          case 3:
            node.textContent = "Message";
            break;
          case 4:
            node.textContent = "rc";
            break;
          case 5:
            node.textContent = "Errors";
            break;
        }
      })

      /*
       * Create summary body.
       */

      summary.tbody.group.node.textContent = this.group;
      summary.tbody.host.node.textContent = this.host;
      summary.tbody.user.node.textContent = this.host_obj["config"]["credentials"]["user"];
      summary.tbody.message.node.textContent = this.host_obj["message"];
      if(this.host_obj["message"] !== "ok")
        summary.tbody.message.node.classList.add("error-red");
      summary.tbody.rc.node.textContent = this.host_obj["rc"];
      summary.tbody.errors.node.textContent = this.host_obj["errors"].length;
      if(this.host_obj["errors"].length > 0)
        summary.tbody.errors.node.classList.add("error-red");

      summary.tbody.node.appendChild(summary.tbody.tr);

      summary.tbody.tr.append(
        summary.tbody.group.node,
        summary.tbody.host.node,
        summary.tbody.user.node,
        summary.tbody.message.node,
        summary.tbody.rc.node,
        summary.tbody.errors.node,
      );

      /*** summary END *******************/

      /*
       * Create errors table.
       */
      const t_errors = {
        table: {
          node: this.ce("table"),
        },
        thead: {
          tr: this.ce("tr"),
          node: this.ce("thead"),
        },
        tbody: {
          node: this.ce("tbody"),
        }
      };

      let th = this.ce("th");
      th.textContent = "Errors";
      t_errors.thead.tr.appendChild(th);

      t_errors.thead.node.appendChild(
        t_errors.thead.tr
      );

      t_errors.table.node.append(
        t_errors.thead.node,
        t_errors.tbody.node
      );

      for(let e in this.host_obj["errors"]) {
        let tr = this.ce("tr");
        let td = this.ce("td");
        td.textContent = this.host_obj["errors"][e];
        tr.appendChild(td);
        t_errors.tbody.node.appendChild(tr);
      }

      /*
       * Create table for settings.
       */
      const settings = {
        table: { 
          node: this.ce("table")
        },
        thead: {
          tr: this.ce("tr"),
          node: this.ce("thead")
        },
        tbody: {
          tr: this.ce("tr"),
          node: this.ce("tbody")
        },
      };

      settings.thead.node.append(settings.thead.tr);
      settings.tbody.node.append(settings.tbody.tr)

      settings.table.node.append(
        settings.thead.node,
        settings.tbody.node,
      );

      for(let k in this.host_obj["config"]["settings"]) {
        // do not add cmds, yet 
        if(k.includes("cmds"))
          continue;
        
        let th = this.ce("th");
        th.textContent = k;
        settings.thead.tr.append(th)
        let td = this.ce("td");
        td.textContent = this.host_obj["config"]["settings"][k]
        settings.tbody.tr.append(td)
      }
      /*** settings table END ************/

      /*
       * Create cmds_before table.
       */
      const cmds_before = this.create_commands_table("cmds_before");
      const cmds_after = this.create_commands_table("cmds_after");
      const conf_cmds = this.create_commands_table("conf_cmds");

      div.append(
        summary.table.node,
        t_errors.table.node,
        settings.table.node,
        cmds_before.table.node,
        cmds_after.table.node,
        conf_cmds.table.node,
      );

      body.appendChild(div);

      /*
       * Set html.
       */
      this.html = body;

    }
    /*** buildHTML END *****************/

    show_html() {
      return new Promise((resolve, reject) => {
        this.contentNode.innerHTML = "";
        this.contentNode.appendChild(
          (this.error) ? this.error : this.html
        );

        resolve("ready");
      });
    }
  }
  /*** class HTMLBuilder END ******************************/

  /*
   * Make Groups expandable
   */
  const all_groups = document.getElementsByClassName("group-entry");
  for(let i = 0; i < all_groups.length; i++) {
    let expander = new Expander(all_groups[i], all_groups[i].nextSibling.nextSibling, "block");
  }

  /*
   * Show report when host clicked.
   */
  const all_lists = document.getElementsByClassName("hosts-nav-sub");
  for(let i = 0; i < all_lists.length; i++) {
    let all_hosts = all_lists[i].getElementsByTagName("li");
    for(let j = 0; j < all_hosts.length; j++) {
      try {
        let builder = new HTMLBuilder(all_hosts[j]);
      }
      catch(e) {
        console.log(e);
      }
    }
  }
  
  /*
   * Filter hosts.
   */
  const filter_hosts =  new FilterHosts();

})();
    </script>
  </body>
</html>
    '''
    """
    Bottom part of the html page that can be generated as a report.
    Yes, it's ugly but it works.
    """

    @staticmethod
    def set_abs_path() -> None:
        """
        Convert :py:class:`~constants.Constants.CHOME`
        to absolute path and set
        :py:class:`~constants.Constants.CHOME_ABS_PATH`.
        """
        Constants.CHOME_ABS_PATH = Path(Constants.CHOME.replace("~", str(Path.home())))
