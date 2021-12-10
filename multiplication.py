'''
[ x0, x1, x2, x3,x4, x5, x6, x7]*[y0, y1, y2, y3, y4, y5, y6,y7]
=[
    x0*y0 + x1*y7 + x2*y6 + x3*y5 + x4*y4 + x5*y3 + x5*y7 + x6*y2 + x6*y6 +
        x6*y7 + x7*y1 + x7*y5 + x7*y6,
    x0*y1 + x1*y0 + x1*y7 + x2*y6 + x2*y7 + x3*y5 + x3*y6 + x4*y4 + x4*y5 +
        x5*y3 + x5*y4 + x5*y7 + x6*y2 + x6*y3 + x6*y6 + x7*y1 + x7*y2 + x7*y5 +
        x7*y7,
    x0*y2 + x1*y1 + x2*y0 + x2*y7 + x3*y6 + x3*y7 + x4*y5 + x4*y6 + x5*y4 +
        x5*y5 + x6*y3 + x6*y4 + x6*y7 + x7*y2 + x7*y3 + x7*y6,
    x0*y3 + x1*y2 + x1*y7 + x2*y1 + x2*y6 + x3*y0 + x3*y5 + x3*y7 + x4*y4 +
        x4*y6 + x4*y7 + x5*y3 + x5*y5 + x5*y6 + x5*y7 + x6*y2 + x6*y4 + x6*y5 +
        x6*y6 + x6*y7 + x7*y1 + x7*y3 + x7*y4 + x7*y5 + x7*y6 + x7*y7,
    x0*y4 + x1*y3 + x1*y7 + x2*y2 + x2*y6 + x2*y7 + x3*y1 + x3*y5 + x3*y6 +
        x4*y0 + x4*y4 + x4*y5 + x4*y7 + x5*y3 + x5*y4 + x5*y6 + x6*y2 + x6*y3 +
        x6*y5 + x7*y1 + x7*y2 + x7*y4 + x7*y7,
    x0*y5 + x1*y4 + x2*y3 + x2*y7 + x3*y2 + x3*y6 + x3*y7 + x4*y1 + x4*y5 +
        x4*y6 + x5*y0 + x5*y4 + x5*y5 + x5*y7 + x6*y3 + x6*y4 + x6*y6 + x7*y2 +
        x7*y3 + x7*y5,
    x0*y6 + x1*y5 + x2*y4 + x3*y3 + x3*y7 + x4*y2 + x4*y6 + x4*y7 + x5*y1 +
        x5*y5 + x5*y6 + x6*y0 + x6*y4 + x6*y5 + x6*y7 + x7*y3 + x7*y4 + x7*y6,
    x0*y7 + x1*y6 + x2*y5 + x3*y4 + x4*y3 + x4*y7 + x5*y2 + x5*y6 + x5*y7 +
        x6*y1 + x6*y5 + x6*y6 + x7*y0 + x7*y4 + x7*y5 + x7*y7
]

下面是输出的表达式，对应输出每个字的次数是 2，2， 3， 3
[
    x1 + x2*x3 + x4 + c,
    x1 + x2*x3 + x2 + x3*x4 + x4,
    x1*x4 + x1 + x2*x3*x4 + x2*x3 + x2 + x3*x4 + x3 + x4^2 + x4*c + x4 + c,
    x1^2 + x1*x2 + x1*x3*x4 + x1*x4 + x1*c + x1 + x2^2*x3^2 + x2^2*x3 +  x2*x3^2*x4 + x2*x3*x4 + x2*x3*c + x2*x3 + x2*x4 + x2*c + x2 + x3*x4^2 + x3*x4*c + x3*x4 + x3
]

'''

