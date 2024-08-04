pragma solidity ^0.5.12;

contract LibNote {
    event LogNote(
        bytes4   indexed  sig,
        address  indexed  usr,
        bytes32  indexed  arg1,
        bytes32  indexed  arg2,
        bytes             data
    ) anonymous;

    modifier note {
        _;
        assembly {
            
            
            let mark := msize                         
            mstore(0x40, add(mark, 288))              
            mstore(mark, 0x20)                        
            mstore(add(mark, 0x20), 224)              
            calldatacopy(add(mark, 0x40), 0, 224)     
            log4(mark, 288,                           
                 shl(224, shr(224, calldataload(0))), 
                 caller,                              
                 calldataload(4),                     
                 calldataload(36)                     
                )
        }
    }
}

contract VatLike {
    function slip(bytes32,address,int) public;
}

contract GemLike5 {
    function decimals() public view returns (uint8);
    function transfer(address,uint) public returns (bool);
    function transferFrom(address,address,uint) public returns (bool);
}

contract GemJoin5 is LibNote {
    
    mapping (address => uint) public wards;
    function rely(address usr) external note auth { wards[usr] = 1; }
    function deny(address usr) external note auth { wards[usr] = 0; }
    modifier auth { require(wards[msg.sender] == 1); _; }

    VatLike  public vat;
    bytes32  public ilk;
    GemLike5 public gem;
    uint     public dec;
    uint     public live;  

    constructor(address vat_, bytes32 ilk_, address gem_) public {
        gem = GemLike5(gem_);
        dec = gem.decimals();
        require(dec < 18, "GemJoin5/decimals-18-or-higher");
        wards[msg.sender] = 1;
        live = 1;
        vat = VatLike(vat_);
        ilk = ilk_;
    }

    function cage() external note auth {
        live = 0;
    }

    function mul(uint x, uint y) internal pure returns (uint z) {
        require(y == 0 || (z = x * y) / y == x, "GemJoin5/overflow");
    }

    function join(address urn, uint wad) public note {
        require(live == 1, "GemJoin5/not-live");
        uint wad18 = mul(wad, 10 ** (18 - dec));
        require(int(wad18) >= 0, "GemJoin5/overflow");
        vat.slip(ilk, urn, int(wad18));
        require(gem.transferFrom(msg.sender, address(this), wad), "GemJoin5/failed-transfer");
    }

    function exit(address guy, uint wad) public note {
        uint wad18 = mul(wad, 10 ** (18 - dec));
        require(int(wad18) >= 0, "GemJoin5/overflow");
        vat.slip(ilk, msg.sender, -int(wad18));
        require(gem.transfer(guy, wad), "GemJoin5/failed-transfer");
    }
}