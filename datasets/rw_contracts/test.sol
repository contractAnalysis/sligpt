
pragma solidity 0.4.25;

contract test{
  bool freezing=true;
  bool flag_add=false;
  bool flag_subtract=false;
  int8 value=0;
  int8 max=10;
  int8 min=1;

  modifier canUpdate() {
    require(!freezing);
    _;
  }
    modifier canAdd() {
    require(flag_add);
    _;
  }

  modifier canSubtract() {
    require(flag_subtract);
    _;
  }
  function setFreezing() public{
    if (freezing){freezing=false;}
    else{freezing=true;}
  }

  function setValue(int8 v, bool flag) internal{
    if (flag){
      require(getValue()+v<=max);
      value+=v;
    }
    else{
      require(getValue()-v>=min);
      value-=v;
    }

  }
  function add(int8 v) public canUpdate canAdd{
      setValue(v,flag_add);
  }

  function subtract(int8 v) public canUpdate canSubtract{
      setValue(v,!flag_subtract);
  }


  function setMax(int8 max_) public{
    max=max_;
  }
    function setMin(int8 min_) public{
    min=min_;
  }

  function updateFlagAdd() public {
    if (getValue()>=max){
      flag_add=false;
    }else{
      flag_add=true;
    }
  }

    function updateFlagSubtract() public {
    if (getValue()<=min){
      flag_subtract=false;
    }else{
      flag_subtract=true;
    }
  }

function getValue() public returns(int8){return value;}


}
