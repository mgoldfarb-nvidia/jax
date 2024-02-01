
from core import *
from lax import *
from api import *

def nd(f, x):
  deriv = (f(x + 0.001) - f(x - 0.001)) * (1.0 / 0.002)
  return f(x), deriv

def f(x):
  y = sin(x) * 2.
  z = - y + x
  return z

f_jaxpr = trace_to_jaxpr(f, (jax_type_of(3.),))

print(f_jaxpr)
print(f(3.0))
print(eval_jaxpr({}, f_jaxpr, (3.,)))

ans, f_lin = linearize_jaxpr(f_jaxpr, (3.0,))
print(ans)
print(f_lin)

print(transpose_linear_jaxpr(f_lin, canonicalize_pyval(1.0)))

print(value_and_grad(f, 3.0))
print(nd(f, 3.0))


def f2(x):
  def when_true():
    return x + x
  def when_false():
    return x * x
  return cond(x > 2.0, when_true, when_false)

print(f2(1.0))
f2_jaxpr = trace_to_jaxpr(f2, (jax_type_of(1.),))
print(f2_jaxpr)
print(eval_jaxpr({}, f2_jaxpr, (1.,)))
print(eval_jaxpr({}, f2_jaxpr, (3.,)))
