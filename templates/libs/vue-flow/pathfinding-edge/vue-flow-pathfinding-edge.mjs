const { defineComponent: Ze, computed: O, useAttrs: Ke, unref: F, openBlock: G, createBlock: Ae, normalizeProps: It, mergeProps: xt, createElementBlock: et, Fragment: tt, createElementVNode: it, normalizeStyle: nt, createCommentVNode: rt } = Vue;
import { useVueFlow as Ct, getSimpleBezierPath as at, BezierEdge as Et, EdgeText as st } from "/libs/vue-flow/core/vue-flow-core.mjs";
var Rt = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, R = {}, jt = {
  get exports() {
    return R;
  },
  set exports(e) {
    R = e;
  }
}, j = {}, Jt = {
  get exports() {
    return j;
  },
  set exports(e) {
    j = e;
  }
}, Me = {}, Lt = {
  get exports() {
    return Me;
  },
  set exports(e) {
    Me = e;
  }
};
(function(e) {
  (function() {
    var t, n, i, r, a, s, u, h, f, c, b, v, g, y, p;
    i = Math.floor, c = Math.min, n = function(o, l) {
      return o < l ? -1 : o > l ? 1 : 0;
    }, f = function(o, l, d, m, k) {
      var A;
      if (d == null && (d = 0), k == null && (k = n), d < 0)
        throw new Error("lo must be non-negative");
      for (m == null && (m = o.length); d < m; )
        A = i((d + m) / 2), k(l, o[A]) < 0 ? m = A : d = A + 1;
      return [].splice.apply(o, [d, d - d].concat(l)), l;
    }, s = function(o, l, d) {
      return d == null && (d = n), o.push(l), y(o, 0, o.length - 1, d);
    }, a = function(o, l) {
      var d, m;
      return l == null && (l = n), d = o.pop(), o.length ? (m = o[0], o[0] = d, p(o, 0, l)) : m = d, m;
    }, h = function(o, l, d) {
      var m;
      return d == null && (d = n), m = o[0], o[0] = l, p(o, 0, d), m;
    }, u = function(o, l, d) {
      var m;
      return d == null && (d = n), o.length && d(o[0], l) < 0 && (m = [o[0], l], l = m[0], o[0] = m[1], p(o, 0, d)), l;
    }, r = function(o, l) {
      var d, m, k, A, M, w;
      for (l == null && (l = n), A = function() {
        w = [];
        for (var N = 0, _ = i(o.length / 2); 0 <= _ ? N < _ : N > _; 0 <= _ ? N++ : N--)
          w.push(N);
        return w;
      }.apply(this).reverse(), M = [], m = 0, k = A.length; m < k; m++)
        d = A[m], M.push(p(o, d, l));
      return M;
    }, g = function(o, l, d) {
      var m;
      if (d == null && (d = n), m = o.indexOf(l), m !== -1)
        return y(o, 0, m, d), p(o, m, d);
    }, b = function(o, l, d) {
      var m, k, A, M, w;
      if (d == null && (d = n), k = o.slice(0, l), !k.length)
        return k;
      for (r(k, d), w = o.slice(l), A = 0, M = w.length; A < M; A++)
        m = w[A], u(k, m, d);
      return k.sort(d).reverse();
    }, v = function(o, l, d) {
      var m, k, A, M, w, N, _, B, C;
      if (d == null && (d = n), l * 10 <= o.length) {
        if (A = o.slice(0, l).sort(d), !A.length)
          return A;
        for (k = A[A.length - 1], _ = o.slice(l), M = 0, N = _.length; M < N; M++)
          m = _[M], d(m, k) < 0 && (f(A, m, 0, null, d), A.pop(), k = A[A.length - 1]);
        return A;
      }
      for (r(o, d), C = [], w = 0, B = c(l, o.length); 0 <= B ? w < B : w > B; 0 <= B ? ++w : --w)
        C.push(a(o, d));
      return C;
    }, y = function(o, l, d, m) {
      var k, A, M;
      for (m == null && (m = n), k = o[d]; d > l; ) {
        if (M = d - 1 >> 1, A = o[M], m(k, A) < 0) {
          o[d] = A, d = M;
          continue;
        }
        break;
      }
      return o[d] = k;
    }, p = function(o, l, d) {
      var m, k, A, M, w;
      for (d == null && (d = n), k = o.length, w = l, A = o[l], m = 2 * l + 1; m < k; )
        M = m + 1, M < k && !(d(o[m], o[M]) < 0) && (m = M), o[l] = o[m], l = m, m = 2 * l + 1;
      return o[l] = A, y(o, w, l, d);
    }, t = function() {
      o.push = s, o.pop = a, o.replace = h, o.pushpop = u, o.heapify = r, o.updateItem = g, o.nlargest = b, o.nsmallest = v;
      function o(l) {
        this.cmp = l ?? n, this.nodes = [];
      }
      return o.prototype.push = function(l) {
        return s(this.nodes, l, this.cmp);
      }, o.prototype.pop = function() {
        return a(this.nodes, this.cmp);
      }, o.prototype.peek = function() {
        return this.nodes[0];
      }, o.prototype.contains = function(l) {
        return this.nodes.indexOf(l) !== -1;
      }, o.prototype.replace = function(l) {
        return h(this.nodes, l, this.cmp);
      }, o.prototype.pushpop = function(l) {
        return u(this.nodes, l, this.cmp);
      }, o.prototype.heapify = function() {
        return r(this.nodes, this.cmp);
      }, o.prototype.updateItem = function(l) {
        return g(this.nodes, l, this.cmp);
      }, o.prototype.clear = function() {
        return this.nodes = [];
      }, o.prototype.empty = function() {
        return this.nodes.length === 0;
      }, o.prototype.size = function() {
        return this.nodes.length;
      }, o.prototype.clone = function() {
        var l;
        return l = new o(), l.nodes = this.nodes.slice(0), l;
      }, o.prototype.toArray = function() {
        return this.nodes.slice(0);
      }, o.prototype.insert = o.prototype.push, o.prototype.top = o.prototype.peek, o.prototype.front = o.prototype.peek, o.prototype.has = o.prototype.contains, o.prototype.copy = o.prototype.clone, o;
    }(), e !== null && e.exports ? e.exports = t : window.Heap = t;
  }).call(Rt);
})(Lt);
(function(e) {
  e.exports = Me;
})(Jt);
function Ht(e, t, n) {
  this.x = e, this.y = t, this.walkable = n === void 0 ? !0 : n;
}
var we = Ht, Yt = {
  Always: 1,
  Never: 2,
  IfAtMostOneObstacle: 3,
  OnlyWhenNoObstacles: 4
}, $ = Yt, ot = we, U = $;
function D(e, t, n) {
  var i;
  typeof e != "object" ? i = e : (t = e.length, i = e[0].length, n = e), this.width = i, this.height = t, this.nodes = this._buildNodes(i, t, n);
}
D.prototype._buildNodes = function(e, t, n) {
  var i, r, a = new Array(t);
  for (i = 0; i < t; ++i)
    for (a[i] = new Array(e), r = 0; r < e; ++r)
      a[i][r] = new ot(r, i);
  if (n === void 0)
    return a;
  if (n.length !== t || n[0].length !== e)
    throw new Error("Matrix size does not fit");
  for (i = 0; i < t; ++i)
    for (r = 0; r < e; ++r)
      n[i][r] && (a[i][r].walkable = !1);
  return a;
};
D.prototype.getNodeAt = function(e, t) {
  return this.nodes[t][e];
};
D.prototype.isWalkableAt = function(e, t) {
  return this.isInside(e, t) && this.nodes[t][e].walkable;
};
D.prototype.isInside = function(e, t) {
  return e >= 0 && e < this.width && t >= 0 && t < this.height;
};
D.prototype.setWalkableAt = function(e, t, n) {
  this.nodes[t][e].walkable = n;
};
D.prototype.getNeighbors = function(e, t) {
  var n = e.x, i = e.y, r = [], a = !1, s = !1, u = !1, h = !1, f = !1, c = !1, b = !1, v = !1, g = this.nodes;
  if (this.isWalkableAt(n, i - 1) && (r.push(g[i - 1][n]), a = !0), this.isWalkableAt(n + 1, i) && (r.push(g[i][n + 1]), u = !0), this.isWalkableAt(n, i + 1) && (r.push(g[i + 1][n]), f = !0), this.isWalkableAt(n - 1, i) && (r.push(g[i][n - 1]), b = !0), t === U.Never)
    return r;
  if (t === U.OnlyWhenNoObstacles)
    s = b && a, h = a && u, c = u && f, v = f && b;
  else if (t === U.IfAtMostOneObstacle)
    s = b || a, h = a || u, c = u || f, v = f || b;
  else if (t === U.Always)
    s = !0, h = !0, c = !0, v = !0;
  else
    throw new Error("Incorrect value of diagonalMovement");
  return s && this.isWalkableAt(n - 1, i - 1) && r.push(g[i - 1][n - 1]), h && this.isWalkableAt(n + 1, i - 1) && r.push(g[i - 1][n + 1]), c && this.isWalkableAt(n + 1, i + 1) && r.push(g[i + 1][n + 1]), v && this.isWalkableAt(n - 1, i + 1) && r.push(g[i + 1][n - 1]), r;
};
D.prototype.clone = function() {
  var e, t, n = this.width, i = this.height, r = this.nodes, a = new D(n, i), s = new Array(i);
  for (e = 0; e < i; ++e)
    for (s[e] = new Array(n), t = 0; t < n; ++t)
      s[e][t] = new ot(t, e, r[e][t].walkable);
  return a.nodes = s, a;
};
var Xt = D, P = {};
function ke(e) {
  for (var t = [[e.x, e.y]]; e.parent; )
    e = e.parent, t.push([e.x, e.y]);
  return t.reverse();
}
P.backtrace = ke;
function Gt(e, t) {
  var n = ke(e), i = ke(t);
  return n.concat(i.reverse());
}
P.biBacktrace = Gt;
function Tt(e) {
  var t, n = 0, i, r, a, s;
  for (t = 1; t < e.length; ++t)
    i = e[t - 1], r = e[t], a = i[0] - r[0], s = i[1] - r[1], n += Math.sqrt(a * a + s * s);
  return n;
}
P.pathLength = Tt;
function Ne(e, t, n, i) {
  var r = Math.abs, a = [], s, u, h, f, c, b;
  for (h = r(n - e), f = r(i - t), s = e < n ? 1 : -1, u = t < i ? 1 : -1, c = h - f; a.push([e, t]), !(e === n && t === i); )
    b = 2 * c, b > -f && (c = c - f, e = e + s), b < h && (c = c + h, t = t + u);
  return a;
}
P.interpolate = Ne;
function Ut(e) {
  var t = [], n = e.length, i, r, a, s, u, h;
  if (n < 2)
    return t;
  for (u = 0; u < n - 1; ++u)
    for (i = e[u], r = e[u + 1], a = Ne(i[0], i[1], r[0], r[1]), s = a.length, h = 0; h < s - 1; ++h)
      t.push(a[h]);
  return t.push(e[n - 1]), t;
}
P.expandPath = Ut;
function zt(e, t) {
  var n = t.length, i = t[0][0], r = t[0][1], a = t[n - 1][0], s = t[n - 1][1], u, h, f, c, b, v, g, y, p, o, l;
  for (u = i, h = r, b = [[u, h]], v = 2; v < n; ++v) {
    for (y = t[v], f = y[0], c = y[1], p = Ne(u, h, f, c), l = !1, g = 1; g < p.length; ++g)
      if (o = p[g], !e.isWalkableAt(o[0], o[1])) {
        l = !0;
        break;
      }
    l && (lastValidCoord = t[v - 1], b.push(lastValidCoord), u = lastValidCoord[0], h = lastValidCoord[1]);
  }
  return b.push([a, s]), b;
}
P.smoothenPath = zt;
function Qt(e) {
  if (e.length < 3)
    return e;
  var t = [], n = e[0][0], i = e[0][1], r = e[1][0], a = e[1][1], s = r - n, u = a - i, h, f, c, b, v, g;
  for (v = Math.sqrt(s * s + u * u), s /= v, u /= v, t.push([n, i]), g = 2; g < e.length; g++)
    h = r, f = a, c = s, b = u, r = e[g][0], a = e[g][1], s = r - h, u = a - f, v = Math.sqrt(s * s + u * u), s /= v, u /= v, (s !== c || u !== b) && t.push([h, f]);
  return t.push([r, a]), t;
}
P.compressPath = Qt;
var T = {
  /**
   * Manhattan distance.
   * @param {number} dx - Difference in x.
   * @param {number} dy - Difference in y.
   * @return {number} dx + dy
   */
  manhattan: function(e, t) {
    return e + t;
  },
  /**
   * Euclidean distance.
   * @param {number} dx - Difference in x.
   * @param {number} dy - Difference in y.
   * @return {number} sqrt(dx * dx + dy * dy)
   */
  euclidean: function(e, t) {
    return Math.sqrt(e * e + t * t);
  },
  /**
   * Octile distance.
   * @param {number} dx - Difference in x.
   * @param {number} dy - Difference in y.
   * @return {number} sqrt(dx * dx + dy * dy) for grids
   */
  octile: function(e, t) {
    var n = Math.SQRT2 - 1;
    return e < t ? n * e + t : n * t + e;
  },
  /**
   * Chebyshev distance.
   * @param {number} dx - Difference in x.
   * @param {number} dy - Difference in y.
   * @return {number} max(dx, dy)
   */
  chebyshev: function(e, t) {
    return Math.max(e, t);
  }
}, Vt = j, qt = P, de = T, z = $;
function lt(e) {
  e = e || {}, this.allowDiagonal = e.allowDiagonal, this.dontCrossCorners = e.dontCrossCorners, this.heuristic = e.heuristic || de.manhattan, this.weight = e.weight || 1, this.diagonalMovement = e.diagonalMovement, this.diagonalMovement || (this.allowDiagonal ? this.dontCrossCorners ? this.diagonalMovement = z.OnlyWhenNoObstacles : this.diagonalMovement = z.IfAtMostOneObstacle : this.diagonalMovement = z.Never), this.diagonalMovement === z.Never ? this.heuristic = e.heuristic || de.manhattan : this.heuristic = e.heuristic || de.octile;
}
lt.prototype.findPath = function(e, t, n, i, r) {
  var a = new Vt(function(A, M) {
    return A.f - M.f;
  }), s = r.getNodeAt(e, t), u = r.getNodeAt(n, i), h = this.heuristic, f = this.diagonalMovement, c = this.weight, b = Math.abs, v = Math.SQRT2, g, y, p, o, l, d, m, k;
  for (s.g = 0, s.f = 0, a.push(s), s.opened = !0; !a.empty(); ) {
    if (g = a.pop(), g.closed = !0, g === u)
      return qt.backtrace(u);
    for (y = r.getNeighbors(g, f), o = 0, l = y.length; o < l; ++o)
      p = y[o], !p.closed && (d = p.x, m = p.y, k = g.g + (d - g.x === 0 || m - g.y === 0 ? 1 : v), (!p.opened || k < p.g) && (p.g = k, p.h = p.h || c * h(b(d - n), b(m - i)), p.f = p.g + p.h, p.parent = g, p.opened ? a.updateItem(p) : (a.push(p), p.opened = !0)));
  }
  return [];
};
var We = lt, ut = We;
function ie(e) {
  ut.call(this, e);
  var t = this.heuristic;
  this.heuristic = function(n, i) {
    return t(n, i) * 1e6;
  };
}
ie.prototype = new ut();
ie.prototype.constructor = ie;
var Zt = ie, Kt = P, pe = $;
function ht(e) {
  e = e || {}, this.allowDiagonal = e.allowDiagonal, this.dontCrossCorners = e.dontCrossCorners, this.diagonalMovement = e.diagonalMovement, this.diagonalMovement || (this.allowDiagonal ? this.dontCrossCorners ? this.diagonalMovement = pe.OnlyWhenNoObstacles : this.diagonalMovement = pe.IfAtMostOneObstacle : this.diagonalMovement = pe.Never);
}
ht.prototype.findPath = function(e, t, n, i, r) {
  var a = [], s = this.diagonalMovement, u = r.getNodeAt(e, t), h = r.getNodeAt(n, i), f, c, b, v, g;
  for (a.push(u), u.opened = !0; a.length; ) {
    if (b = a.shift(), b.closed = !0, b === h)
      return Kt.backtrace(h);
    for (f = r.getNeighbors(b, s), v = 0, g = f.length; v < g; ++v)
      c = f[v], !(c.closed || c.opened) && (a.push(c), c.opened = !0, c.parent = b);
  }
  return [];
};
var ei = ht, ft = We;
function ne(e) {
  ft.call(this, e), this.heuristic = function(t, n) {
    return 0;
  };
}
ne.prototype = new ft();
ne.prototype.constructor = ne;
var ti = ne, Ge = j, Te = P, ge = T, Q = $;
function ct(e) {
  e = e || {}, this.allowDiagonal = e.allowDiagonal, this.dontCrossCorners = e.dontCrossCorners, this.diagonalMovement = e.diagonalMovement, this.heuristic = e.heuristic || ge.manhattan, this.weight = e.weight || 1, this.diagonalMovement || (this.allowDiagonal ? this.dontCrossCorners ? this.diagonalMovement = Q.OnlyWhenNoObstacles : this.diagonalMovement = Q.IfAtMostOneObstacle : this.diagonalMovement = Q.Never), this.diagonalMovement === Q.Never ? this.heuristic = e.heuristic || ge.manhattan : this.heuristic = e.heuristic || ge.octile;
}
ct.prototype.findPath = function(e, t, n, i, r) {
  var a = function(_, B) {
    return _.f - B.f;
  }, s = new Ge(a), u = new Ge(a), h = r.getNodeAt(e, t), f = r.getNodeAt(n, i), c = this.heuristic, b = this.diagonalMovement, v = this.weight, g = Math.abs, y = Math.SQRT2, p, o, l, d, m, k, A, M, w = 1, N = 2;
  for (h.g = 0, h.f = 0, s.push(h), h.opened = w, f.g = 0, f.f = 0, u.push(f), f.opened = N; !s.empty() && !u.empty(); ) {
    for (p = s.pop(), p.closed = !0, o = r.getNeighbors(p, b), d = 0, m = o.length; d < m; ++d)
      if (l = o[d], !l.closed) {
        if (l.opened === N)
          return Te.biBacktrace(p, l);
        k = l.x, A = l.y, M = p.g + (k - p.x === 0 || A - p.y === 0 ? 1 : y), (!l.opened || M < l.g) && (l.g = M, l.h = l.h || v * c(g(k - n), g(A - i)), l.f = l.g + l.h, l.parent = p, l.opened ? s.updateItem(l) : (s.push(l), l.opened = w));
      }
    for (p = u.pop(), p.closed = !0, o = r.getNeighbors(p, b), d = 0, m = o.length; d < m; ++d)
      if (l = o[d], !l.closed) {
        if (l.opened === w)
          return Te.biBacktrace(l, p);
        k = l.x, A = l.y, M = p.g + (k - p.x === 0 || A - p.y === 0 ? 1 : y), (!l.opened || M < l.g) && (l.g = M, l.h = l.h || v * c(g(k - e), g(A - t)), l.f = l.g + l.h, l.parent = p, l.opened ? u.updateItem(l) : (u.push(l), l.opened = N));
      }
  }
  return [];
};
var _e = ct, dt = _e;
function re(e) {
  dt.call(this, e);
  var t = this.heuristic;
  this.heuristic = function(n, i) {
    return t(n, i) * 1e6;
  };
}
re.prototype = new dt();
re.prototype.constructor = re;
var ii = re, Ue = P, be = $;
function pt(e) {
  e = e || {}, this.allowDiagonal = e.allowDiagonal, this.dontCrossCorners = e.dontCrossCorners, this.diagonalMovement = e.diagonalMovement, this.diagonalMovement || (this.allowDiagonal ? this.dontCrossCorners ? this.diagonalMovement = be.OnlyWhenNoObstacles : this.diagonalMovement = be.IfAtMostOneObstacle : this.diagonalMovement = be.Never);
}
pt.prototype.findPath = function(e, t, n, i, r) {
  var a = r.getNodeAt(e, t), s = r.getNodeAt(n, i), u = [], h = [], f, c, b, v = this.diagonalMovement, g = 0, y = 1, p, o;
  for (u.push(a), a.opened = !0, a.by = g, h.push(s), s.opened = !0, s.by = y; u.length && h.length; ) {
    for (b = u.shift(), b.closed = !0, f = r.getNeighbors(b, v), p = 0, o = f.length; p < o; ++p)
      if (c = f[p], !c.closed) {
        if (c.opened) {
          if (c.by === y)
            return Ue.biBacktrace(b, c);
          continue;
        }
        u.push(c), c.parent = b, c.opened = !0, c.by = g;
      }
    for (b = h.shift(), b.closed = !0, f = r.getNeighbors(b, v), p = 0, o = f.length; p < o; ++p)
      if (c = f[p], !c.closed) {
        if (c.opened) {
          if (c.by === g)
            return Ue.biBacktrace(c, b);
          continue;
        }
        h.push(c), c.parent = b, c.opened = !0, c.by = y;
      }
  }
  return [];
};
var ni = pt, gt = _e;
function ae(e) {
  gt.call(this, e), this.heuristic = function(t, n) {
    return 0;
  };
}
ae.prototype = new gt();
ae.prototype.constructor = ae;
var ri = ae, ve = T, ze = we, V = $;
function bt(e) {
  e = e || {}, this.allowDiagonal = e.allowDiagonal, this.dontCrossCorners = e.dontCrossCorners, this.diagonalMovement = e.diagonalMovement, this.heuristic = e.heuristic || ve.manhattan, this.weight = e.weight || 1, this.trackRecursion = e.trackRecursion || !1, this.timeLimit = e.timeLimit || 1 / 0, this.diagonalMovement || (this.allowDiagonal ? this.dontCrossCorners ? this.diagonalMovement = V.OnlyWhenNoObstacles : this.diagonalMovement = V.IfAtMostOneObstacle : this.diagonalMovement = V.Never), this.diagonalMovement === V.Never ? this.heuristic = e.heuristic || ve.manhattan : this.heuristic = e.heuristic || ve.octile;
}
bt.prototype.findPath = function(e, t, n, i, r) {
  var a = new Date().getTime(), s = function(p, o) {
    return this.heuristic(Math.abs(o.x - p.x), Math.abs(o.y - p.y));
  }.bind(this), u = function(p, o) {
    return p.x === o.x || p.y === o.y ? 1 : Math.SQRT2;
  }, h = function(p, o, l, d, m) {
    if (this.timeLimit > 0 && new Date().getTime() - a > this.timeLimit * 1e3)
      return 1 / 0;
    var k = o + s(p, c) * this.weight;
    if (k > l)
      return k;
    if (p == c)
      return d[m] = [p.x, p.y], p;
    var A, M, w, N, _ = r.getNeighbors(p, this.diagonalMovement);
    for (w = 0, A = 1 / 0; N = _[w]; ++w) {
      if (this.trackRecursion && (N.retainCount = N.retainCount + 1 || 1, N.tested !== !0 && (N.tested = !0)), M = h(N, o + u(p, N), l, d, m + 1), M instanceof ze)
        return d[m] = [p.x, p.y], M;
      this.trackRecursion && --N.retainCount === 0 && (N.tested = !1), M < A && (A = M);
    }
    return A;
  }.bind(this), f = r.getNodeAt(e, t), c = r.getNodeAt(n, i), b = s(f, c), v, g, y;
  for (v = 0; ; ++v) {
    if (g = [], y = h(f, 0, b, g, 0), y === 1 / 0)
      return [];
    if (y instanceof ze)
      return g;
    b = y;
  }
  return [];
};
var ai = bt, si = j, Qe = P, vt = T;
function Be(e) {
  e = e || {}, this.heuristic = e.heuristic || vt.manhattan, this.trackJumpRecursion = e.trackJumpRecursion || !1;
}
Be.prototype.findPath = function(e, t, n, i, r) {
  var a = this.openList = new si(function(f, c) {
    return f.f - c.f;
  }), s = this.startNode = r.getNodeAt(e, t), u = this.endNode = r.getNodeAt(n, i), h;
  for (this.grid = r, s.g = 0, s.f = 0, a.push(s), s.opened = !0; !a.empty(); ) {
    if (h = a.pop(), h.closed = !0, h === u)
      return Qe.expandPath(Qe.backtrace(u));
    this._identifySuccessors(h);
  }
  return [];
};
Be.prototype._identifySuccessors = function(e) {
  var t = this.grid, n = this.heuristic, i = this.openList, r = this.endNode.x, a = this.endNode.y, s, u, h, f, c, b = e.x, v = e.y, g, y, p, o, l, d = Math.abs;
  for (s = this._findNeighbors(e), f = 0, c = s.length; f < c; ++f)
    if (u = s[f], h = this._jump(u[0], u[1], b, v), h) {
      if (g = h[0], y = h[1], l = t.getNodeAt(g, y), l.closed)
        continue;
      p = vt.octile(d(g - b), d(y - v)), o = e.g + p, (!l.opened || o < l.g) && (l.g = o, l.h = l.h || n(d(g - r), d(y - a)), l.f = l.g + l.h, l.parent = e, l.opened ? i.updateItem(l) : (i.push(l), l.opened = !0));
    }
};
var se = Be, mt = se, oi = $;
function J(e) {
  mt.call(this, e);
}
J.prototype = new mt();
J.prototype.constructor = J;
J.prototype._jump = function(e, t, n, i) {
  var r = this.grid, a = e - n, s = t - i;
  if (!r.isWalkableAt(e, t))
    return null;
  if (this.trackJumpRecursion === !0 && (r.getNodeAt(e, t).tested = !0), r.getNodeAt(e, t) === this.endNode)
    return [e, t];
  if (a !== 0) {
    if (r.isWalkableAt(e, t - 1) && !r.isWalkableAt(e - a, t - 1) || r.isWalkableAt(e, t + 1) && !r.isWalkableAt(e - a, t + 1))
      return [e, t];
  } else if (s !== 0) {
    if (r.isWalkableAt(e - 1, t) && !r.isWalkableAt(e - 1, t - s) || r.isWalkableAt(e + 1, t) && !r.isWalkableAt(e + 1, t - s))
      return [e, t];
    if (this._jump(e + 1, t, e, t) || this._jump(e - 1, t, e, t))
      return [e, t];
  } else
    throw new Error("Only horizontal and vertical movements are allowed");
  return this._jump(e + a, t + s, e, t);
};
J.prototype._findNeighbors = function(e) {
  var t = e.parent, n = e.x, i = e.y, r = this.grid, a, s, u, h, f = [], c, b, v, g;
  if (t)
    a = t.x, s = t.y, u = (n - a) / Math.max(Math.abs(n - a), 1), h = (i - s) / Math.max(Math.abs(i - s), 1), u !== 0 ? (r.isWalkableAt(n, i - 1) && f.push([n, i - 1]), r.isWalkableAt(n, i + 1) && f.push([n, i + 1]), r.isWalkableAt(n + u, i) && f.push([n + u, i])) : h !== 0 && (r.isWalkableAt(n - 1, i) && f.push([n - 1, i]), r.isWalkableAt(n + 1, i) && f.push([n + 1, i]), r.isWalkableAt(n, i + h) && f.push([n, i + h]));
  else
    for (c = r.getNeighbors(e, oi.Never), v = 0, g = c.length; v < g; ++v)
      b = c[v], f.push([b.x, b.y]);
  return f;
};
var li = J, At = se, ui = $;
function L(e) {
  At.call(this, e);
}
L.prototype = new At();
L.prototype.constructor = L;
L.prototype._jump = function(e, t, n, i) {
  var r = this.grid, a = e - n, s = t - i;
  if (!r.isWalkableAt(e, t))
    return null;
  if (this.trackJumpRecursion === !0 && (r.getNodeAt(e, t).tested = !0), r.getNodeAt(e, t) === this.endNode)
    return [e, t];
  if (a !== 0 && s !== 0) {
    if (r.isWalkableAt(e - a, t + s) && !r.isWalkableAt(e - a, t) || r.isWalkableAt(e + a, t - s) && !r.isWalkableAt(e, t - s))
      return [e, t];
    if (this._jump(e + a, t, e, t) || this._jump(e, t + s, e, t))
      return [e, t];
  } else if (a !== 0) {
    if (r.isWalkableAt(e + a, t + 1) && !r.isWalkableAt(e, t + 1) || r.isWalkableAt(e + a, t - 1) && !r.isWalkableAt(e, t - 1))
      return [e, t];
  } else if (r.isWalkableAt(e + 1, t + s) && !r.isWalkableAt(e + 1, t) || r.isWalkableAt(e - 1, t + s) && !r.isWalkableAt(e - 1, t))
    return [e, t];
  return this._jump(e + a, t + s, e, t);
};
L.prototype._findNeighbors = function(e) {
  var t = e.parent, n = e.x, i = e.y, r = this.grid, a, s, u, h, f = [], c, b, v, g;
  if (t)
    a = t.x, s = t.y, u = (n - a) / Math.max(Math.abs(n - a), 1), h = (i - s) / Math.max(Math.abs(i - s), 1), u !== 0 && h !== 0 ? (r.isWalkableAt(n, i + h) && f.push([n, i + h]), r.isWalkableAt(n + u, i) && f.push([n + u, i]), r.isWalkableAt(n + u, i + h) && f.push([n + u, i + h]), r.isWalkableAt(n - u, i) || f.push([n - u, i + h]), r.isWalkableAt(n, i - h) || f.push([n + u, i - h])) : u === 0 ? (r.isWalkableAt(n, i + h) && f.push([n, i + h]), r.isWalkableAt(n + 1, i) || f.push([n + 1, i + h]), r.isWalkableAt(n - 1, i) || f.push([n - 1, i + h])) : (r.isWalkableAt(n + u, i) && f.push([n + u, i]), r.isWalkableAt(n, i + 1) || f.push([n + u, i + 1]), r.isWalkableAt(n, i - 1) || f.push([n + u, i - 1]));
  else
    for (c = r.getNeighbors(e, ui.Always), v = 0, g = c.length; v < g; ++v)
      b = c[v], f.push([b.x, b.y]);
  return f;
};
var hi = L, Mt = se, fi = $;
function H(e) {
  Mt.call(this, e);
}
H.prototype = new Mt();
H.prototype.constructor = H;
H.prototype._jump = function(e, t, n, i) {
  var r = this.grid, a = e - n, s = t - i;
  if (!r.isWalkableAt(e, t))
    return null;
  if (this.trackJumpRecursion === !0 && (r.getNodeAt(e, t).tested = !0), r.getNodeAt(e, t) === this.endNode)
    return [e, t];
  if (a !== 0 && s !== 0) {
    if (this._jump(e + a, t, e, t) || this._jump(e, t + s, e, t))
      return [e, t];
  } else if (a !== 0) {
    if (r.isWalkableAt(e, t - 1) && !r.isWalkableAt(e - a, t - 1) || r.isWalkableAt(e, t + 1) && !r.isWalkableAt(e - a, t + 1))
      return [e, t];
  } else if (s !== 0 && (r.isWalkableAt(e - 1, t) && !r.isWalkableAt(e - 1, t - s) || r.isWalkableAt(e + 1, t) && !r.isWalkableAt(e + 1, t - s)))
    return [e, t];
  return r.isWalkableAt(e + a, t) && r.isWalkableAt(e, t + s) ? this._jump(e + a, t + s, e, t) : null;
};
H.prototype._findNeighbors = function(e) {
  var t = e.parent, n = e.x, i = e.y, r = this.grid, a, s, u, h, f = [], c, b, v, g;
  if (t)
    if (a = t.x, s = t.y, u = (n - a) / Math.max(Math.abs(n - a), 1), h = (i - s) / Math.max(Math.abs(i - s), 1), u !== 0 && h !== 0)
      r.isWalkableAt(n, i + h) && f.push([n, i + h]), r.isWalkableAt(n + u, i) && f.push([n + u, i]), r.isWalkableAt(n, i + h) && r.isWalkableAt(n + u, i) && f.push([n + u, i + h]);
    else {
      var y;
      if (u !== 0) {
        y = r.isWalkableAt(n + u, i);
        var p = r.isWalkableAt(n, i + 1), o = r.isWalkableAt(n, i - 1);
        y && (f.push([n + u, i]), p && f.push([n + u, i + 1]), o && f.push([n + u, i - 1])), p && f.push([n, i + 1]), o && f.push([n, i - 1]);
      } else if (h !== 0) {
        y = r.isWalkableAt(n, i + h);
        var l = r.isWalkableAt(n + 1, i), d = r.isWalkableAt(n - 1, i);
        y && (f.push([n, i + h]), l && f.push([n + 1, i + h]), d && f.push([n - 1, i + h])), l && f.push([n + 1, i]), d && f.push([n - 1, i]);
      }
    }
  else
    for (c = r.getNeighbors(e, fi.OnlyWhenNoObstacles), v = 0, g = c.length; v < g; ++v)
      b = c[v], f.push([b.x, b.y]);
  return f;
};
var ci = H, kt = se, di = $;
function Y(e) {
  kt.call(this, e);
}
Y.prototype = new kt();
Y.prototype.constructor = Y;
Y.prototype._jump = function(e, t, n, i) {
  var r = this.grid, a = e - n, s = t - i;
  if (!r.isWalkableAt(e, t))
    return null;
  if (this.trackJumpRecursion === !0 && (r.getNodeAt(e, t).tested = !0), r.getNodeAt(e, t) === this.endNode)
    return [e, t];
  if (a !== 0 && s !== 0) {
    if (r.isWalkableAt(e - a, t + s) && !r.isWalkableAt(e - a, t) || r.isWalkableAt(e + a, t - s) && !r.isWalkableAt(e, t - s))
      return [e, t];
    if (this._jump(e + a, t, e, t) || this._jump(e, t + s, e, t))
      return [e, t];
  } else if (a !== 0) {
    if (r.isWalkableAt(e + a, t + 1) && !r.isWalkableAt(e, t + 1) || r.isWalkableAt(e + a, t - 1) && !r.isWalkableAt(e, t - 1))
      return [e, t];
  } else if (r.isWalkableAt(e + 1, t + s) && !r.isWalkableAt(e + 1, t) || r.isWalkableAt(e - 1, t + s) && !r.isWalkableAt(e - 1, t))
    return [e, t];
  return r.isWalkableAt(e + a, t) || r.isWalkableAt(e, t + s) ? this._jump(e + a, t + s, e, t) : null;
};
Y.prototype._findNeighbors = function(e) {
  var t = e.parent, n = e.x, i = e.y, r = this.grid, a, s, u, h, f = [], c, b, v, g;
  if (t)
    a = t.x, s = t.y, u = (n - a) / Math.max(Math.abs(n - a), 1), h = (i - s) / Math.max(Math.abs(i - s), 1), u !== 0 && h !== 0 ? (r.isWalkableAt(n, i + h) && f.push([n, i + h]), r.isWalkableAt(n + u, i) && f.push([n + u, i]), (r.isWalkableAt(n, i + h) || r.isWalkableAt(n + u, i)) && f.push([n + u, i + h]), !r.isWalkableAt(n - u, i) && r.isWalkableAt(n, i + h) && f.push([n - u, i + h]), !r.isWalkableAt(n, i - h) && r.isWalkableAt(n + u, i) && f.push([n + u, i - h])) : u === 0 ? r.isWalkableAt(n, i + h) && (f.push([n, i + h]), r.isWalkableAt(n + 1, i) || f.push([n + 1, i + h]), r.isWalkableAt(n - 1, i) || f.push([n - 1, i + h])) : r.isWalkableAt(n + u, i) && (f.push([n + u, i]), r.isWalkableAt(n, i + 1) || f.push([n + u, i + 1]), r.isWalkableAt(n, i - 1) || f.push([n + u, i - 1]));
  else
    for (c = r.getNeighbors(e, di.IfAtMostOneObstacle), v = 0, g = c.length; v < g; ++v)
      b = c[v], f.push([b.x, b.y]);
  return f;
};
var pi = Y, me = $, gi = li, bi = hi, vi = ci, mi = pi;
function Ai(e) {
  return e = e || {}, e.diagonalMovement === me.Never ? new gi(e) : e.diagonalMovement === me.Always ? new bi(e) : e.diagonalMovement === me.OnlyWhenNoObstacles ? new vi(e) : new mi(e);
}
var Mi = Ai, ki = {
  Heap: j,
  Node: we,
  Grid: Xt,
  Util: P,
  DiagonalMovement: $,
  Heuristic: T,
  AStarFinder: We,
  BestFirstFinder: Zt,
  BreadthFirstFinder: ei,
  DijkstraFinder: ti,
  BiAStarFinder: _e,
  BiBestFirstFinder: ii,
  BiBreadthFirstFinder: ni,
  BiDijkstraFinder: ri,
  IDAStarFinder: ai,
  JumpPointFinder: Mi
};
(function(e) {
  e.exports = ki;
})(jt);
function ye(e, t) {
  switch (t) {
    case "top":
      return { x: e.x, y: e.y - 1 };
    case "bottom":
      return { x: e.x, y: e.y + 1 };
    case "left":
      return { x: e.x - 1, y: e.y };
    case "right":
      return { x: e.x + 1, y: e.y };
  }
}
function Ve(e, t, n) {
  let i = e.getNodeAt(t.x, t.y);
  for (; !i.walkable; ) {
    e.setWalkableAt(i.x, i.y, !0);
    const r = ye(i, n);
    i = e.getNodeAt(r.x, r.y);
  }
}
const W = 10;
function q(e, t, n) {
  let i = e.x / W, r = e.y / W, a = t / W, s = n / W;
  if (a < 1)
    for (; a !== 1; )
      a++, i++;
  else if (a > 1)
    for (; a !== 1; )
      a--, i--;
  if (s < 1)
    for (; s !== 1; )
      s++, r++;
  else if (s > 1)
    for (; s !== 1; )
      s--, r--;
  return { x: i, y: r };
}
function yi(e, t, n) {
  let i = e.x * W, r = e.y * W, a = t, s = n;
  if (a < W)
    for (; a !== W; )
      a = a + W, i = i - W;
  else if (a > W)
    for (; a !== W; )
      a = a - W, i = i + W;
  if (s < W)
    for (; s !== W; )
      s = s + W, r = r - W;
  else if (s > W)
    for (; s !== W; )
      s = s - W, r = r + W;
  return { x: i, y: r };
}
function Z(e, t = 10) {
  return Math.round(e / t) * t;
}
function K(e, t = 10) {
  return Math.floor(e / t) * t;
}
function ee(e, t = 10) {
  return Math.ceil(e / t) * t;
}
const x = 10;
function wi(e, t, n, i) {
  const { xMin: r, yMin: a, width: s, height: u } = e, h = s / x, f = u / x, c = new R.Grid(h, f);
  t.forEach((l) => {
    const d = q(l.topLeft, r, a), m = q(l.bottomRight, r, a);
    for (let k = d.x; k < m.x; k++)
      for (let A = d.y; A < m.y; A++)
        c.setWalkableAt(k, A, !1);
  });
  const b = q(
    {
      x: Z(n.x, x),
      y: Z(n.y, x)
    },
    r,
    a
  ), v = q(
    {
      x: Z(i.x, x),
      y: Z(i.y, x)
    },
    r,
    a
  ), g = c.getNodeAt(b.x, b.y);
  Ve(c, g, n.position);
  const y = c.getNodeAt(v.x, v.y);
  Ve(c, y, i.position);
  const p = ye(g, n.position), o = ye(y, i.position);
  return { grid: c, start: p, end: o };
}
function Ni(e, t, n, i) {
  const r = (e - n) / 2 + n, a = (t - i) / 2 + i;
  return [r, a];
}
function Wi(e) {
  let i = e[0];
  const r = e[0];
  let a = `M${r[0]},${r[1]}M`;
  for (let u = 0; u < e.length; u++) {
    const h = e[u], f = Ni(i[0], i[1], h[0], h[1]);
    a += ` ${f[0]},${f[1]}`, a += `Q${h[0]},${h[1]}`, i = h;
  }
  const s = e[e.length - 1];
  return a += ` ${s[0]},${s[1]}`, a;
}
function _i(e, t, n) {
  const i = [[e.x, e.y], ...n, [t.x, t.y]];
  return Wi(i);
}
function Bi(e, t, n) {
  const i = new R.AStarFinder({
    diagonalMovement: R.DiagonalMovement.Always,
    allowDiagonal: !0,
    dontCrossCorners: !0
  });
  let r = [];
  try {
    r = i.findPath(t.x, t.y, n.x, n.y, e), r = R.Util.smoothenPath(e, r);
  } catch {
  }
  return r;
}
function Fi(e, t = 0, n = 0, i = 0) {
  t = Math.max(Math.round(t), 0), n = Math.max(Math.round(n), 0), i = Math.max(Math.round(i), 0), t = Number.isInteger(t) ? t : 0, n = Number.isInteger(n) ? n : 0, i = Number.isInteger(i) ? i : 0;
  let r = Number.MIN_SAFE_INTEGER, a = Number.MIN_SAFE_INTEGER, s = Number.MAX_SAFE_INTEGER, u = Number.MAX_SAFE_INTEGER;
  const h = e.map((o) => {
    const {
      computedPosition: { x: l, y: d },
      dimensions: m
    } = o, k = Math.max(m.width || 0, 1), A = Math.max(m.height || 0, 1), M = {
      x: l || 0,
      y: d || 0
    }, w = {
      x: M.x - t,
      y: M.y - t
    }, N = {
      x: M.x - t,
      y: M.y + A + t
    }, _ = {
      x: M.x + k + t,
      y: M.y - t
    }, B = {
      x: M.x + k + t,
      y: M.y + A + t
    };
    return i > 0 && (w.x = K(w.x, i), w.y = K(w.y, i), N.x = K(N.x, i), N.y = ee(N.y, i), _.x = ee(_.x, i), _.y = K(_.y, i), B.x = ee(B.x, i), B.y = ee(B.y, i)), w.y < u && (u = w.y), w.x < s && (s = w.x), B.y > a && (a = B.y), B.x > r && (r = B.x), {
      id: o.id,
      width: k,
      height: A,
      topLeft: w,
      bottomLeft: N,
      topRight: _,
      bottomRight: B
    };
  });
  r = r + n, a = a + n, s = s - n, u = u - n;
  const f = {
    x: s,
    y: u
  }, c = {
    x: s,
    y: a
  }, b = {
    x: r,
    y: u
  }, v = {
    x: r,
    y: a
  }, g = Math.abs(f.x - b.x), y = Math.abs(f.y - c.y);
  return { nodes: h, graph: {
    topLeft: f,
    bottomLeft: c,
    topRight: b,
    bottomRight: v,
    width: g,
    height: y,
    xMax: r,
    yMax: a,
    xMin: s,
    yMin: u
  } };
}
const Pi = ["d", "marker-end", "marker-start"], $i = {
  name: "PathFindingEdge",
  compatConfig: { MODE: 3 },
  inheritAttrs: !1
}, Li = /* @__PURE__ */ Ze({
  ...$i,
  props: {
    id: null,
    source: null,
    target: null,
    sourceX: null,
    sourceY: null,
    targetX: null,
    targetY: null,
    selected: { type: Boolean, default: !1 },
    animated: { type: Boolean },
    sourcePosition: { default: "bottom" },
    targetPosition: { default: "top" },
    label: null,
    labelStyle: { default: () => ({}) },
    labelShowBg: { type: Boolean, default: !0 },
    labelBgStyle: { default: () => ({}) },
    labelBgPadding: null,
    labelBgBorderRadius: null,
    style: null,
    markerEnd: null,
    markerStart: null,
    sourceHandleId: null,
    targetHandleId: null
  },
  setup(e) {
    const t = e, n = 10, i = 20, r = x, { getNodes: a } = Ct(), s = O(
      () => at({
        ...t
      })
    ), u = O(() => ({
      x: t.sourceX,
      y: t.sourceY,
      position: t.sourcePosition
    })), h = O(() => ({
      x: t.targetX,
      y: t.targetY,
      position: t.targetPosition
    })), f = O(() => Fi(a.value, n, i, r)), c = O(() => {
      let g = [];
      if (h.value.x && u.value.x && a.value.length) {
        const { grid: y, start: p, end: o } = wi(f.value.graph, f.value.nodes, u.value, h.value);
        g = Bi(y, p, o);
      }
      return g;
    }), b = O(() => {
      var y;
      let g = "";
      if ((y = c.value) != null && y.length) {
        const p = c.value.map((o) => {
          const [l, d] = o, m = yi({ x: l, y: d }, f.value.graph.xMin, f.value.graph.yMin);
          return [m.x, m.y];
        });
        g = _i(u.value, h.value, p);
      }
      return g;
    }), v = Ke();
    return (g, y) => F(c) && F(c).length <= 2 ? (G(), Ae(F(Et), It(xt({ key: 0 }, { ...t, ...F(v) })), null, 16)) : (G(), et(tt, { key: 1 }, [
      it("path", {
        style: nt({ ...t.style, ...F(v).style }),
        class: "vue-flow__edge-path",
        d: F(b),
        "marker-end": t.markerEnd,
        "marker-start": t.markerStart
      }, null, 12, Pi),
      t.label ? (G(), Ae(F(st), {
        key: 0,
        x: F(s)[1],
        y: F(s)[2],
        label: t.label,
        "label-style": t.labelStyle,
        "label-show-bg": t.labelShowBg,
        "label-bg-style": t.labelBgStyle,
        "label-bg-padding": t.labelBgPadding,
        "label-bg-border-radius": t.labelBgBorderRadius
      }, null, 8, ["x", "y", "label", "label-style", "label-show-bg", "label-bg-style", "label-bg-padding", "label-bg-border-radius"])) : rt("", !0)
    ], 64));
  }
});
var Di = Math.PI;
function Oi(e, t, n, i) {
  i === void 0 && (i = !1);
  var r = t[0], a = t[1], s = n[0], u = n[1], h = s + (e - r) / (a - r) * (u - s);
  if (i === !0)
    if (s < u) {
      if (h < s)
        return s;
      if (h > u)
        return u;
    } else {
      if (h > s)
        return s;
      if (h < u)
        return u;
    }
  return h;
}
function qe(e, t, n, i, r) {
  var a = Math.sin(r), s = Math.cos(r), u = e - n, h = t - i, f = u * s - h * a, c = u * a + h * s;
  return [f + n, c + i];
}
function Si(e, t, n, i) {
  return Math.hypot(i - t, n - e);
}
function X(e, t, n, i) {
  return Math.atan2(i - t, n - e);
}
function te(e, t, n, i) {
  return [Math.cos(n) * i + e, Math.sin(n) * i + t];
}
function E(e, t, n, i, r) {
  return r === void 0 && (r = 0.5), [e + (n - e) * r, t + (i - t) * r];
}
function Ii(e, t) {
  return t === void 0 && (t = 8), Math.floor(t * (0.5 + e / (Di * 2) % t));
}
function xi(e, t, n, i) {
  return Math.abs((n - e) / 2 / ((i - t) / 2));
}
function Ci(e, t, n, i, r) {
  r === void 0 && (r = {});
  var a = r, s = a.bow, u = s === void 0 ? 0 : s, h = a.stretch, f = h === void 0 ? 0.5 : h, c = a.stretchMin, b = c === void 0 ? 0 : c, v = a.stretchMax, g = v === void 0 ? 420 : v, y = a.padStart, p = y === void 0 ? 0 : y, o = a.padEnd, l = o === void 0 ? 0 : o, d = a.flip, m = d === void 0 ? !1 : d, k = a.straights, A = k === void 0 ? !0 : k, M = X(e, t, n, i), w = Si(e, t, n, i), N = xi(e, t, n, i);
  if (w < (p + l) * 2 || u === 0 && f === 0 || A && [0, 1, 1 / 0].includes(N)) {
    var _ = Math.max(0, Math.min(w - p, p)), B = Math.max(0, Math.min(w - _, l)), C = te(e, t, M, _), Fe = C[0], Pe = C[1], $e = te(n, i, M + Math.PI, B), De = $e[0], Oe = $e[1], Se = E(Fe, Pe, De, Oe, 0.5), yt = Se[0], wt = Se[1];
    return [Fe, Pe, yt, wt, De, Oe, M, M, M];
  }
  var Ie = (Ii(M) % 2 === 0 ? 1 : -1) * (m ? -1 : 1), xe = u + Oi(w, [b, g], [1, 0], !0) * f, Ce = E(e, t, n, i, 0.5), Nt = Ce[0], Wt = Ce[1], Ee = E(e, t, n, i, 0.5 - xe), S = Ee[0], I = Ee[1], Re = qe(S, I, Nt, Wt, Math.PI / 2 * Ie);
  S = Re[0], I = Re[1];
  var _t = X(e, t, S, I), je = te(e, t, _t, p), oe = je[0], le = je[1], Bt = X(n, i, S, I), Je = te(n, i, Bt, l), ue = Je[0], he = Je[1], Ft = X(S, I, e, t), Pt = X(S, I, n, i), Le = E(oe, le, ue, he, 0.5), $t = Le[0], Dt = Le[1], He = E(oe, le, ue, he, 0.5 - xe), fe = He[0], ce = He[1], Ye = qe(fe, ce, $t, Dt, Math.PI / 2 * Ie);
  fe = Ye[0], ce = Ye[1];
  var Xe = E(S, I, fe, ce, 0.5), Ot = Xe[0], St = Xe[1];
  return [oe, le, Ot, St, ue, he, Pt, Ft, M];
}
const Ei = ["d", "marker-end", "marker-start"], Ri = {
  name: "PerfectArrow",
  compatConfig: { MODE: 3 },
  inheritAttrs: !1
}, Hi = /* @__PURE__ */ Ze({
  ...Ri,
  props: {
    id: null,
    source: null,
    target: null,
    sourceX: null,
    sourceY: null,
    targetX: null,
    targetY: null,
    selected: { type: Boolean },
    animated: { type: Boolean },
    sourcePosition: null,
    targetPosition: null,
    label: null,
    labelStyle: null,
    labelShowBg: { type: Boolean },
    labelBgStyle: null,
    labelBgPadding: null,
    labelBgBorderRadius: null,
    style: null,
    markerEnd: null,
    markerStart: null,
    sourceHandleId: null,
    targetHandleId: null,
    options: { default: () => ({
      padStart: 3,
      padEnd: 3,
      stretch: 0.2
    }) }
  },
  setup(e) {
    const t = e, n = O(
      () => at({
        ...t
      })
    ), i = O(() => Ci(t.sourceX, t.sourceY, t.targetX, t.targetY, {
      ...t.options
    })), r = Ke();
    return (a, s) => (G(), et(tt, null, [
      it("path", {
        style: nt({ ...t.style, ...F(r).style }),
        class: "vue-flow__edge-path vue-flow__perfect-arrow",
        d: `M${F(i)[0]},${F(i)[1]} Q${F(i)[2]},${F(i)[3]} ${F(i)[4]},${F(i)[5]}`,
        "marker-end": t.markerEnd,
        "marker-start": t.markerStart
      }, null, 12, Ei),
      t.label ? (G(), Ae(F(st), {
        key: 0,
        x: F(n)[1],
        y: F(n)[2],
        label: t.label,
        "label-style": t.labelStyle,
        "label-show-bg": t.labelShowBg,
        "label-bg-style": t.labelBgStyle,
        "label-bg-padding": t.labelBgPadding,
        "label-bg-border-radius": t.labelBgBorderRadius
      }, null, 8, ["x", "y", "label", "label-style", "label-show-bg", "label-bg-style", "label-bg-padding", "label-bg-border-radius"])) : rt("", !0)
    ], 64));
  }
});
export {
  Li as PathFindingEdge,
  Hi as PerfectArrow
};
