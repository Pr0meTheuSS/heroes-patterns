#pragma once

#include "unit_state.h"

class UnitContext {
public:
    UnitContext(UnitState* state)
        : state_(nullptr)
    {
        this->TransitionTo(state);
    }
    // TODO: change to smart-pointer
    ~UnitContext() { delete state_; }

    void TransitionTo(UnitState* state)
    {
        if (this->state_ != nullptr) {
            delete this->state_;
        }
        this->state_ = state;
        this->state_->setContext(this);
    }

private:
    UnitState* state_;
};
