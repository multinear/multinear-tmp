import{S as A,z as $,A as J,B as w,C as Q,d as P,U as h,D as x,g as y,E as q,F as W,G as X,H as k,I as ee,J as C,K,L as M,h as L,M as re,O as ne,P as ie,Q as se,R as te,T as U,V as ae,W as fe,X as ue,q as F,Y as le,Z as ce,_ as de,a0 as V,a1 as oe,a2 as Y,a3 as T,a4 as ve,a5 as _e,a6 as j,a7 as he,a8 as pe,a9 as be,aa as ye,x as H,i as we,ab as Pe,ac as ge}from"./index-client.CTjIiTiR.js";import{g as Re}from"./disclose-version.DJKRdGjo.js";function I(e,r=null,t){if(typeof e!="object"||e===null||A in e)return e;const f=X(e);if(f!==$&&f!==J)return e;var s=new Map,l=k(e),_=w(0);l&&s.set("length",w(e.length));var v;return new Proxy(e,{defineProperty(u,n,i){(!("value"in i)||i.configurable===!1||i.enumerable===!1||i.writable===!1)&&Q();var a=s.get(n);return a===void 0?(a=w(i.value),s.set(n,a)):P(a,I(i.value,v)),!0},deleteProperty(u,n){var i=s.get(n);if(i===void 0)n in u&&s.set(n,w(h));else{if(l&&typeof n=="string"){var a=s.get("length"),c=Number(n);Number.isInteger(c)&&c<a.v&&P(a,c)}P(i,h),Z(_)}return!0},get(u,n,i){var p;if(n===A)return e;var a=s.get(n),c=n in u;if(a===void 0&&(!c||(p=x(u,n))!=null&&p.writable)&&(a=w(I(c?u[n]:h,v)),s.set(n,a)),a!==void 0){var d=y(a);return d===h?void 0:d}return Reflect.get(u,n,i)},getOwnPropertyDescriptor(u,n){var i=Reflect.getOwnPropertyDescriptor(u,n);if(i&&"value"in i){var a=s.get(n);a&&(i.value=y(a))}else if(i===void 0){var c=s.get(n),d=c==null?void 0:c.v;if(c!==void 0&&d!==h)return{enumerable:!0,configurable:!0,value:d,writable:!0}}return i},has(u,n){var d;if(n===A)return!0;var i=s.get(n),a=i!==void 0&&i.v!==h||Reflect.has(u,n);if(i!==void 0||q!==null&&(!a||(d=x(u,n))!=null&&d.writable)){i===void 0&&(i=w(a?I(u[n],v):h),s.set(n,i));var c=y(i);if(c===h)return!1}return a},set(u,n,i,a){var O;var c=s.get(n),d=n in u;if(l&&n==="length")for(var p=i;p<c.v;p+=1){var b=s.get(p+"");b!==void 0?P(b,h):p in u&&(b=w(h),s.set(p+"",b))}c===void 0?(!d||(O=x(u,n))!=null&&O.writable)&&(c=w(void 0),P(c,I(i,v)),s.set(n,c)):(d=c.v!==h,P(c,I(i,v)));var g=Reflect.getOwnPropertyDescriptor(u,n);if(g!=null&&g.set&&g.set.call(a,i),!d){if(l&&typeof n=="string"){var m=s.get("length"),R=Number(n);Number.isInteger(R)&&R>=m.v&&P(m,R+1)}Z(_)}return!0},ownKeys(u){y(_);var n=Reflect.ownKeys(u).filter(c=>{var d=s.get(c);return d===void 0||d.v!==h});for(var[i,a]of s)a.v!==h&&!(i in u)&&n.push(i);return n},setPrototypeOf(){W()}})}function Z(e,r=1){P(e,e.v+r)}function Te(e,r,t,f=null,s=!1){L&&re();var l=e,_=null,v=null,u=null,n=s?ne:0;ee(()=>{if(u===(u=!!r()))return;let i=!1;if(L){const a=l.data===ie;u===a&&(l=se(),te(l),U(!1),i=!0)}u?(_?C(_):_=K(()=>t(l)),v&&M(v,()=>{v=null})):(v?C(v):f&&(v=K(()=>f(l))),_&&M(_,()=>{_=null})),i&&U(!0)},n),L&&(l=ae)}function z(e,r){return e===r||(e==null?void 0:e[A])===r}function me(e={},r,t,f){return fe(()=>{var s,l;return ue(()=>{s=l,l=[],F(()=>{e!==t(...l)&&(r(e,...l),s&&z(t(...s),e)&&r(null,...s))})}),()=>{le(()=>{l&&z(t(...l),e)&&r(null,...l)})}}),e}const Ee={get(e,r){if(!e.exclude.includes(r))return y(e.version),r in e.special?e.special[r]():e.props[r]},set(e,r,t){return r in e.special||(e.special[r]=xe({get[r](){return e.props[r]}},r,V)),e.special[r](t),Y(e.version),!0},getOwnPropertyDescriptor(e,r){if(!e.exclude.includes(r)&&r in e.props)return{enumerable:!0,configurable:!0,value:e.props[r]}},deleteProperty(e,r){return e.exclude.includes(r)||(e.exclude.push(r),Y(e.version)),!0},has(e,r){return e.exclude.includes(r)?!1:r in e.props},ownKeys(e){return Reflect.ownKeys(e.props).filter(r=>!e.exclude.includes(r))}};function Ae(e,r){return new Proxy({props:e,exclude:r,special:{},version:w(0)},Ee)}const Ie={get(e,r){let t=e.props.length;for(;t--;){let f=e.props[t];if(T(f)&&(f=f()),typeof f=="object"&&f!==null&&r in f)return f[r]}},set(e,r,t){let f=e.props.length;for(;f--;){let s=e.props[f];T(s)&&(s=s());const l=x(s,r);if(l&&l.set)return l.set(t),!0}return!1},getOwnPropertyDescriptor(e,r){let t=e.props.length;for(;t--;){let f=e.props[t];if(T(f)&&(f=f()),typeof f=="object"&&f!==null&&r in f){const s=x(f,r);return s&&!s.configurable&&(s.configurable=!0),s}}},has(e,r){for(let t of e.props)if(T(t)&&(t=t()),t!=null&&r in t)return!0;return!1},ownKeys(e){const r=[];for(let t of e.props){T(t)&&(t=t());for(const f in t)r.includes(f)||r.push(f)}return r}};function De(...e){return new Proxy({props:e},Ie)}function G(e){for(var r=q,t=q;r!==null&&!(r.f&(ve|_e));)r=r.parent;try{return j(r),e()}finally{j(t)}}function xe(e,r,t,f){var B;var s=(t&he)!==0,l=!pe||(t&be)!==0,_=(t&ye)!==0,v=(t&Pe)!==0,u=!1,n;_?[n,u]=Re(()=>e[r]):n=e[r];var i=(B=x(e,r))==null?void 0:B.set,a=f,c=!0,d=!1,p=()=>(d=!0,c&&(c=!1,v?a=F(f):a=f),a);n===void 0&&f!==void 0&&(i&&l&&ce(),n=p(),i&&i(n));var b;if(l)b=()=>{var o=e[r];return o===void 0?p():(c=!0,d=!1,o)};else{var g=G(()=>(s?H:we)(()=>e[r]));g.f|=de,b=()=>{var o=y(g);return o!==void 0&&(a=void 0),o===void 0?a:o}}if(!(t&V))return b;if(i){var m=e.$$legacy;return function(o,E){return arguments.length>0?((!l||!E||m||u)&&i(E?b():o),o):b()}}var R=!1,O=!1,D=ge(n),S=G(()=>H(()=>{var o=b(),E=y(D);return R?(R=!1,O=!0,E):(O=!1,D.v=o)}));return s||(S.equals=oe),function(o,E){if(arguments.length>0){const N=E?y(S):l&&_?I(o):o;return S.equals(N)||(R=!0,P(D,N),d&&a!==void 0&&(a=N),F(()=>y(S))),o}return y(S)}}export{I as a,me as b,Te as i,Ae as l,xe as p,De as s};