#pragma once

class UnitContext;

class UnitState {
public:
    virtual ~UnitState() = default;

    void setContext(UnitContext* context) { this->context_ = context; }

protected:
    UnitContext* context_;
};
