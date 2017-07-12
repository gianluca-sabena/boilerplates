//
// Created by Gianluca on 10/04/2017.
//

#include<iostream>

// See book: The C++ Programming Language (4th Edition) - section 2.2.5

int main(){

    int ar1[10] = {0,1,2,3,4,5,6,7,8,9};
    //int ar2[10] = {0,10,20,30,40,50};
    int* pv3 = nullptr;

    int val3 = ar1[3]; // copy value
    pv3 = &ar1[3]; // prefix unary & means ‘‘address of.’’
    int contv3 = *pv3; // prefix unary ∗ means ‘‘contents of’’
    int& ref3 = ar1[3]; // unary suffix & means ‘‘reference to.’’

    // A reference is similar to a pointer, except that you don’t need to use a prefix ∗ to access the value
    // referred to by the reference. Also, a reference cannot be made to refer to a different object after its initialization.

    std::cout << "Array ar1: ";
    for (auto& x : ar1) // for each x in v
        std::cout << ++x << ", ";
    std::cout << std::endl << std::endl;

    std::cout << "Pointer to ar1[3]: " << pv3 << std::endl;
    std::cout << "Content of pointer to ar1[3]: " << contv3 << std::endl;
    std::cout << "Reference to ar1[3]: " << ref3 << std::endl;
    std::cout << "Value of ar1[3]: " << val3 << std::endl << std::endl;
    std::cout << "UPDATE value of ar1[3] to 30" << std::endl << std::endl;
    ar1[3] = 30;
    std::cout << "Pointer to ar1[3]: " << pv3 << std::endl;
    std::cout << "Content of pointer to ar1[3]: " << contv3 << std::endl;
    std::cout << "Reference to ar1[3]: " << ref3 << std::endl;
    std::cout << "Value of ar1[3]: " << val3 << std::endl;



    //    for (auto i=0; i!=10; ++i) {
    //        std::cout << ar1[i] << ",";
    //    }
}

//
//            OUTPUT:
//
//            Array ar1: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
//
//            Pointer to ar1[3]: 0x7fff55699afc
//            Content of pointer to ar1[3]: 3
//            Reference to ar1[3]: 3
//            Value of ar1[3]: 3
//
//            UPDATE value of ar1[3] to 30
//
//            Pointer to ar1[3]: 0x7fff55699afc
//            Content of pointer to ar1[3]: 3
//            Reference to ar1[3]: 30
//            Value of ar1[3]: 3