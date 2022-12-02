function App() {
    let self = this;

    // MODEL


    // type Page = Login | Loading | User | Admin
    self.email = ko.observable("");
    self.passwd = ko.observable("");
    self.binancePairs = ko.observableArray([]);
    self.forexPairs = ko.observableArray([]);
    self.oandaPairs = ko.observableArray([]);
    self.binanceApiKey = ko.observable("");
    self.binanceSecretKey = ko.observable("");
    self.forexUsername = ko.observable("");
    self.forexPassword = ko.observable("");
    self.forexApiKey = ko.observable("");
    self.oandaAcctId = ko.observable("");
    self.oandaApiKey = ko.observable("");
    self.loginErr = ko.observable("");
    self.users = ko.observableArray([]);
    self.newUserEmail = ko.observable("");
    self.newUserPassword = ko.observable("");
    self.newPairLabel = ko.observable("");
    self.newPairExchange = ko.observable("");
    self.pairs = ko.observableArray([]);

    {% if current_user.is_authenticated %}

    self.page = ko.observable("Loading");

    {% if current_user.hasRole("admin") %}

    self.isAdmin = ko.observable(true);

    {% else %}

    self.isAdmin = ko.observable(false);

    {% endif %}

    {% else %}

    self.page = ko.observable("Login");
    self.isAdmin = ko.observable(false);

    {% endif %}

    self.pairDir = ko.observable("");


    // UDPATE


    self.loginButtonClick = () => {
        self.page("Loading");
        self.loginErr("");
        const encodedLoginForm = {
            email: self.email(),
            passwd: self.passwd()
        };
        self.email("");
        self.passwd("");
        userLogin(encodedLoginForm);
    }

    self.userSavePassword = () => {
        self.page("Loading");
        savePassword(self.passwd());
    }
    
    self.userSaveBinance = () => {
        self.page("Loading")
        const binance = {
          apiKey: self.binanceApiKey(), 
          secretKey: self.binanceSecretKey(),
        };
        self.binanceApiKey("");
        self.binanceSecretKey("");
        saveBinance(binance);
    }

    self.userSaveForex = () => {
        self.page("Loading");
        const forex = {
          username: self.forexUsername(),
          password: self.forexPassword(),
          apiKey: self.forexApiKey(),
        };
        self.forexUsername("");
        self.forexPassword("");
        self.forexApiKey("");
        saveForex(forex);
    }

    self.userSaveOanda = () => {
        self.page("Loading");
        const oanda = {
            acctId: self.oandaAcctId(),
            apiKey: self.oandaApiKey(),
        };
        self.oandaAcctId("");
        self.oandaApiKey("");
        saveOanda(oanda);
    }

    self.adminPage = () => {    
        self.page("Loading");
        getUsers();
        getPairs();
    }

    self.adminBack = () => {
        self.page("User");
    }
    
    self.userLogout = () => {
        self.page("Loading");
        userLogout()
    }

    self.startSaveUserPairs = () => {
        self.page("Loading");
        saveUserPairs();
    }
    
    self.addNewUser = () => {
        self.page("Loading");
        const newUser = {
          email : self.newUserEmail(),
          passwd : self.newUserPassword()
        };
        self.newUserEmail("");
        self.newUserPassword("");
        saveNewUser(newUser);
    }
    //Inner template functions      


    self.addForexPair = item => {
        item.forex.pairs.push({label: item.forex.box()});
        item.forex.box("")
        item.forex.isAverse()
    }

    self.addBinancePair = item => {
      item.binance.pairs.push({label: item.binance.box()});
      item.binance.box("")
      item.binance.isAverse()
    }
    
    self.addOandaPair = item => {
      item.oanda.pairs.push({label: item.oanda.box()});
      item.oanda.box("")
      item.oanda.isAverse()
    }

    adminSaveUser = user => {
      self.page("Loading");
      adminUpdateUser(user);
    }

    self.addNewPair = () => {
      self.page("Loading");
      const newPair = {
        label: self.newPairLabel(),
        exchange: self.newPairExchange(),
        trend: "",
        confirmation: "",
        trig: "",
      }
      self.newPairLabel("");
      self.newPairExchange("");
      saveNewPair(newPair);
    }
    
    updatePair = pair => {
      self.page("Loading");
      savePair(pair);
    }

    // HTTP


    const userLogin = async loginForm => {
        const res = await jaxPost("{{url_for('login')}}", loginForm);
        if (res.ok === false) {
            echo("res");
            echo(res);
            self.loginErr(res.data);
            self.page("Login");
        } else {
            self.isAdmin(res.isAdmin)
            getUserPairs();
        }
    }
    
    const saveUserPairs = async () => {
      const encodePairs = i => ({
          label: i.label,
          orderSize: i.box(),
          isAverse: i.isAverse(),
      });

      const payload = {
        forexPairs: self.forexPairs().map(encodePairs),
        binancePairs: self.binancePairs().map(encodePairs),
        oandaPairs: self.oandaPairs().map(encodePairs),
      }
      const res = await jaxPut("{{url_for('users.pairs')}}", payload);
      self.page("User");
    }

    const getUserPairs = async () => {
      const res = await jaxGet("{{url_for('users.user')}}");
      const decodePairs = i => ({
          label: i.label,
          box: ko.observable(i.orderSize),
          isAverse: ko.observable(i.isAverse),
      });

      self.forexPairs(res.forexPairs.map(decodePairs));
      self.binancePairs(res.binancePairs.map(decodePairs));
      self.oandaPairs(res.oandaPairs.map(decodePairs));

      self.page("User");  
    }

    const savePassword = async passwd => {
        const res = await jaxPut("{{url_for('users.passwd')}}", passwd);
        self.page("User");
    }

    const saveBinance = async binance => {
        const res = await jaxPut("{{url_for('users.binance')}}", binance);
        self.page("User");
    }    

    const saveForex = async forex => {
        const res = await jaxPut("{{url_for('users.forex')}}", forex);
        self.page("User");
    }
    
    const saveOanda = async oanda => {
        const res = await jaxPut("{{url_for('users.oanda')}}", oanda);
        self.page("User");
    }

    const userLogout = async () => {
        const res = await jaxGet("{{url_for('logout')}}");
        self.page("Login");
    }

    const getUsers = async () => {
        const res = await jaxGet("{{url_for('users.index')}}");
        const dropPair = (userEmail, k) => item => {
            const userList = self.users();
            for (let x=0; x < userList.length; x++) {
              if (userList[x].email === userEmail) {
                userList[x][k].pairs.remove(item);
              }
            }
        }

        const decodeUsers = i => ({
            id: i.id,
            email: i.email,
            passwd: ko.observable(""),
            binance : {
              apiKey: i.binance.apiKey,
              secretKey: i.binance.secretKey,
              pairs: ko.observableArray(i.binance.pairs),
              box: ko.observable(""),
              isAverse: ko.observable(i.isAverse),
              deletePair: dropPair(i.email, "binance"),
            },
            forex : {
              username: i.forex.username,
              password: i.forex.password,
              apiKey: i.forex.apiKey,
              pairs: ko.observableArray(i.forex.pairs),
              box: ko.observable(""),
              isAverse: ko.observable(i.isAverse),
              deletePair: dropPair(i.email, "forex"),
            },
            oanda : {
                accountId: i.oanda.acctId,
                apiKey: i.oanda.apiKey,
                pairs: ko.observableArray(i.oanda.pairs),
                box: ko.observable(""),
                isAverse: ko.observable(i.isAverse),
                deletePair: dropPair(i.email, "oanda"),
            },
            isAdmin: ko.observable(i.admin),
        });
      
        self.users(res.map(decodeUsers));
    }
    
  const getPairs = async () => {
    const res = await jaxGet("{{url_for('pairs.index')}}");
    const dropPair = (pairLabel) => item =>{
      self.pairs.remove(item);
    }

    const decodePairs = i => ({
      label: i.label,
      exchange: i.exchange,
      trend: ko.observable(i.trend),
      confirmation: ko.observable(i.confirmation),
      trig: ko.observable(i.trig),
      deletePair: dropPair(i.label),
    });
    self.pairs(res.map(decodePairs));
    self.page("Admin");
  }

  
    const adminUpdateUser = async user => {
      const encodeUser = {
        id: user.id,
        passwd: user.passwd(),
        binance: user.binance.pairs(),
        forex: user.forex.pairs(),
        oanda: user.oanda.pairs(),
        isAdmin: user.isAdmin(),
      };
      const res = await jaxPut("{{url_for('users.adminUpdate')}}", encodeUser);
      echo(res)
      self.adminPage();
    }

    const saveNewUser = async newUser => {
      const res = await jaxPost("{{url_for('users.adminSaveNewUser')}}", newUser);
      echo("res");
      echo(res);
      self.adminPage()
    }
    
    const saveNewPair = async newPair => {
      const res = await jaxPost("{{url_for('pairs.createPair')}}", newPair);
      echo("res");
      echo(res);
      self.adminPage();
    }

    const savePair = async pair => {
      const encodePair = {
        label: pair.label,
        exchange: pair.exchange,
        trend: pair.trend(),
        confirmation: pair.confirmation(),
        trig: pair.trig(),
      }
      const res = await jaxPut("{{url_for('pairs.updatePair')}}", encodePair);
      echo(res);
      self.adminPage();
    }
    // INIT

    {% if current_user.is_authenticated %}
    getUserPairs()
    {% endif %}


}
