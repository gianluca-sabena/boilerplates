//
// Created by Gianluca on 11/04/2017.
//

#include <iostream>

struct VectorStruct {
    int sz; // number of elements
    double *elem; // pointer to elements
};


void vector_init(VectorStruct &v, int s) {
    v.elem = new double[s];
    v.sz = s;
}

class Vector {
public:
    // member initializer list
    Vector(int s) : elem{new double[s]}, sz{s} {
        std::cout<< "Vector created with " << s << " elements" << std::endl;
    }

    // element access: subscripting - http://www.learncpp.com/cpp-tutorial/98-overloading-the-subscript-operator/
    double& operator[](int i) {
        return elem[i];
    }

    int size() {
        return sz;
    }

private:
    int sz;       // the number of elements
    double *elem; // pointer to the elements

};


int main() {
    VectorStruct vs;
    vector_init(vs, 10);

    Vector vc(6);

    std::cout<< "Elements 4 is: "<< vc.operator[](4);
    std::cout<< "Elements 4 is: "<< vc[4];


}