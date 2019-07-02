pragma solidity ^0.5.0;


contract Purchasing {
    // declarations

    struct item {
        address payable owner;
        uint amount;
        uint barcode;
        uint price;
        bool forSale;
    }

    mapping (uint => item) public items; // map hashes of (owner, barcode) pairs to items
                                         // key = sha256(abi.encodePacked(owner, barcode))
    
    // events
    event Payment(address _to, address _from, uint amount);
    
    // functions
    function pay(address payable _to, uint amount) public payable {
        require(amount > 0, "amount too small");
        _to.transfer(amount);
        emit Payment(msg.sender, _to, amount);
    }

    function getHash(address owner, uint barcode) internal pure returns (uint hash) {
        return uint(sha256(abi.encodePacked(owner, barcode)));
    }

    function addItem(uint amount, uint barcode, uint price) public {
        item memory it;
        it.owner = msg.sender;
        it.amount = amount;
        it.barcode = barcode;
        it.price = price;
        it.forSale = true;
        items[getHash(msg.sender, barcode)] = it;
    }

    function buyItem(address owner, uint barcode, uint _amount) payable public {
        item storage it = items[getHash(owner, barcode)];
        item storage newIt = items[getHash(msg.sender, barcode)];
        // Make sure there is enough stock
        require(it.amount >= _amount, "not enough stock");
        // require the amount / item to exist
        require(it.amount > 0, " item does not exist");
        require(_amount > 0, "amount must be positive");
        require(it.forSale, "item is not for sale");
        // user must pay current owner in ether
        it.owner.transfer(it.price * _amount);
        // make new ownership of purchased good
        newIt.owner = msg.sender;
        it.amount -= _amount;
        newIt.amount += _amount;
        newIt.barcode = it.barcode;
        newIt.forSale = false;
    }
    
    
    function deleteItem(uint barcode, uint amount) public {
        item storage it = items[getHash(msg.sender, barcode)];
        // only the seller can delete their own items
        require(it.owner == msg.sender);
        it.amount -= amount;
        if (it.amount <= 0) {
            it.amount = 0;
        }
    }

    function putUpForSale(uint barcode) public {
        item storage it = items[getHash(msg.sender, barcode)];
        require(it.amount > 0, "item has no amount or does not exist");
        it.forSale = true;
    }
    
    function takeDownFromSale(uint barcode) public {
        item storage it = items[getHash(msg.sender, barcode)];
        require(it.amount > 0, "item has no amount or does not exist");
        it.forSale = false;
    }
    
    function changePrice(uint barcode, uint price) public {
        item storage it = items[getHash(msg.sender, barcode)];
        require(it.amount > 0, "item has no amount or does not exist");
        it.price = price;
    }

    function getAmount(address owner, uint barcode) public view returns (uint amount){
        item storage it = items[getHash(owner, barcode)];
        return it.amount;
    }
    
    function getPrice(address owner, uint barcode) public view returns (uint price){
        item storage it = items[getHash(owner, barcode)];
        return it.price;
    }
	
	function isForSale(address owner, uint barcode) public view returns (bool forSale) {
		item storage it = items[getHash(owner, barcode)];
		return it.forSale;
	}
}