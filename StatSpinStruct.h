#ifndef _STATSPINSTRUCT_H
#define _STATSPINSTRUCT_H
#include "MatrixQuantity.h"
#include "defs.h"

class StatSpinStruct : public MatrixQuantity
{
    public:
        StatSpinStruct(const Stepper* stepper,
                       FileManager* fm, bool meas_trans=false);
        virtual ~StatSpinStruct() {}
        virtual void measure();
    private:
        bool isup(const std::vector<uint_vec_t>& in);
        bool isdo(const std::vector<uint_vec_t>& in);
        bool m_meas_trans;
};

#endif//_STATSPINSTRUCT_H
