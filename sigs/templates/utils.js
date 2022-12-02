const echo = a => { console.log(a); return a; }
const jaxCfg = (method, data) => ({
    method,
    body: JSON.stringify(data),
    cache: "no-cache",
    headers: new Headers({"content-type": "application/json"}),
    credentials: "same-origin",
});

const jaxGet = url => fetch(url, jaxCfg("GET", undefined))
    .then(res => res.json());

const jaxPost = (url, data) => fetch(url, jaxCfg("POST", data))
    .then(res => res.json());

const jaxPut = (url, data) => fetch(url, jaxCfg("PUT", data))
    .then(res => res.json());
