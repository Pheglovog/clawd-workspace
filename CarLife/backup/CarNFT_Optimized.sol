// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CarNFT - Optimized for Security
 * @author Pheglovog
 * @notice 改进版 CarNFT 智能合约，添加 Pausable、AccessControl 和安全优化
 * @dev This is the optimized version for testing
 */

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/extensions/AccessControlEnumerable.sol";

contract CarNFT is ERC721, ERC721Enumerable, Pausable, AccessControlEnumerable {
    // ====== 状态变量 ======

    bool private _paused;
    bool private _mintingPaused;

    // 角色定义
    bytes32 public constant DEFAULT_ADMIN_ROLE = keccak256("DEFAULT_ADMIN_ROLE");
    bytes32 public constant PROVIDER_ROLE = keccak256("PROVIDER_ROLE");

    // 车辆信息（用于 Gas 优化）
    mapping(uint256 => CarInfo) private _carInfos;
    uint256 public totalCars;
    uint256 public constant MAX_CARS_PER_TX = 10; // 每次交易最多查询 10 辆车

    // 车辆信息结构
    struct CarInfo {
        string make;          // 品牌
        string model;         // 型号
        uint256 mileage;     // 里程
        string condition;      // 状况（excellent, good, fair, poor）
        uint256 lastServiceDate;
        address owner;
    }

    // ====== 事件 ======

    event Paused(address indexed account);
    event Unpaused(address indexed account);
    event MintingPaused(address indexed account);
    event MintingUnpaused(address indexed account);
    event MaintenanceAdded(uint256 indexed tokenId, uint256 mileage, string notes, address indexed provider);
    event RoleGranted(address indexed account, bytes32 indexed role);
    event RoleRevoked(address indexed account, bytes32 indexed role);

    // ====== 构造函数 ======

    constructor() ERC721("CarLife NFT", "CLFT") {
        _grantRole(msg.sender, DEFAULT_ADMIN_ROLE);

        // 授予调用者管理员权限（可选）
        if (msg.sender != owner())) {
            _setRoleAdmin(msg.sender, PROVIDER_ROLE);
        }
    }

    // ====== Pausable 功能 ======

    /**
     * @dev 当合约暂停时，所有转账、mint 操作都被禁用
     */
    function pause() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
        emit Paused(msg.sender);
    }

    function unpause() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
        emit Unpaused(msg.sender);
    }

    function pauseMinting() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _mintingPaused = true;
        emit MintingPaused(msg.sender);
    }

    function unpauseMinting() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _mintingPaused = false;
        emit MintingUnpaused(msg.sender);
    }

    // ====== 重写 Pausable 函数添加检查 ======

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256
    ) internal override whenNotPaused whenNotPausedMinting {
        require(!_isBlacklisted(from), "Sender is blacklisted");
        require(!_isBlacklisted(to), "Recipient is blacklisted");
        require(!paused || _isAuthorized(from), "From is not authorized or paused");
        require(!paused || _isAuthorized(to), "To is not authorized or paused");
        super._beforeTokenTransfer(from, to, 0);
    }

    function _beforeTokenTransfer(
        address from,
        address,
        uint256
    ) internal override whenNotPaused {
        require(!_isBlacklisted(from), "Sender is blacklisted");
        require(!_isBlacklisted(to), "Recipient is blacklisted");
        require(!paused || _isAuthorized(from), "From is not authorized or paused");
        require(!paused || _isAuthorized(to), "To is not authorized or paused");
    }

    // ====== 访问控制增强 ======

    /**
     * @dev 检查地址是否有特定角色
     */
    function _hasRole(bytes32 role, address account) internal view returns (bool) {
        return super.hasRole(role, account);
    }

    /**
     * @dev 检查地址是否被授权
     */
    function _isAuthorized(address account) internal view returns (bool) {
        // 管理员始终被授权
        if (account == owner()) {
            return true;
        }
        // 检查角色
        return _hasRole(DEFAULT_ADMIN_ROLE, account) || _hasRole(PROVIDER_ROLE, account);
    }

    /**
     * @dev 检查地址是否在黑名单
     */
    function _isBlacklisted(address account) internal view returns (bool) {
        return _isBlacklisted[account];
    }

    // ====== 修改器（添加修饰器） ======

    /**
     * @dev 使用安全修改器确保只有授权用户可以修改车辆信息
     */
    modifier onlyAuthorizedOrProvider() {
        require(_isAuthorized(msg.sender) || _isProvider(msg.sender), "Not authorized");
        _;
    }

    modifier onlyAdmin() {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Only admin");
        _;
    }

    // ====== 车辆信息管理（Gas 优化） ======

    /**
     * @dev 添加或更新车辆信息（仅授权用户）
     * Gas 优化：使用 mapping 而非数组
     */
    function addCarInfo(
        uint256 tokenId,
        string memory make,
        string memory model,
        uint256 mileage,
        string memory condition,
        string memory notes
    ) public onlyAuthorizedOrProvider {
        require(tokenId < totalSupply(), "Token does not exist");
        
        _carInfos[tokenId] = CarInfo({
            make: make,
            model: model,
            mileage: mileage,
            condition: condition,
            lastServiceDate: block.timestamp,
            owner: msg.sender
        });
        
        emit MaintenanceAdded(tokenId, mileage, notes, msg.sender);
    }

    /**
     * @dev 批量查询车辆信息（Gas 优化版本）
     * 限制每次最多查询 MAX_CARS_PER_TX 辆车
     */
    function getCarInfo(uint256 tokenId) public view returns (CarInfo memory) {
        require(tokenId < totalSupply(), "Token does not exist");
        return _carInfos[tokenId];
    }

    /**
     * @dev 批量查询（优化版）
     * @param startTokenId 起始 token ID（包含）
     * @param count 查询数量（不超过 MAX_CARS_PER_TX）
     */
    function getCarInfoBatch(uint256 startTokenId, uint256 count) 
        public 
        view 
        returns (CarInfo[] memory carInfoArray) 
    {
        require(startTokenId < totalSupply(), "Invalid start token");
        require(count > 0 && count <= MAX_CARS_PER_TX, "Invalid count");

        carInfoArray = new CarInfo[](count);
        
        uint256 endTokenId = startTokenId + count;
        require(endTokenId <= totalSupply(), "End token out of bounds");

        for (uint256 i = 0; i < count; i++) {
            uint256 tokenId = startTokenId + i;
            carInfoArray[i] = _carInfos[tokenId];
        }

        return carInfoArray;
    }

    /**
     * @dev 更新车辆信息（仅授权用户）
     */
    function updateCarInfo(
        uint256 tokenId,
        string memory make,
        string memory model,
        uint256 mileage,
        string memory condition,
        string memory notes
    ) public onlyAuthorizedOrProvider {
        require(tokenId < totalSupply(), "Token does not exist");
        
        _carInfos[tokenId] = CarInfo({
            make: make,
            model: model,
            mileage: mileage,
            condition: condition,
            lastServiceDate: block.timestamp,
            owner: msg.sender
        });
        
        emit MaintenanceAdded(tokenId, mileage, notes, msg.sender);
    }

    /**
     * @dev 获取车辆总数
     */
    function getTotalCars() public view returns (uint256) {
        return totalCars;
    }

    // ====== 批量铸造（优化） ======

    /**
     * @dev 批量铸造 NFT（Gas 优化）
     * 限制每次最多铸造 MAX_CARS_PER_TX 个
     * @param to 铸入地址
     * @param tokenIds 质车对应的 token ID 数组
     */
    function mintBatch(
        address to,
        uint256[] memory tokenIds
    ) public onlyAuthorizedOrProvider whenNotPaused {
        require(tokenIds.length > 0 && tokenIds.length <= MAX_CARS_PER_TX, 
                "Invalid token count");
        require(tokenIds.length <= totalSupply(), "Invalid token count");

        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            
            // 检查是否已存在（防止重复铸造）
            if (_exists(tokenId)) {
                revert("Token already minted");
            }
            
            _mint(to, tokenId);
        }

        // ====== 管理员功能 ======

    /**
     * @dev 添加黑名单（仅管理员）
     */
    function addToBlacklist(address account) public onlyAdmin {
        _isBlacklisted[account] = true;
    }

    /**
     * @dev 从黑名单移除（仅管理员）
     */
    function removeFromBlacklist(address account) public onlyAdmin {
        _isBlacklisted[account] = false;
    }

    /**
     * @dev 检查地址是否在黑名单
     */
    function isBlacklisted(address account) public view returns (bool) {
        return _isBlacklisted[account];
    }

    /**
     * @dev 授予提供商角色（仅管理员）
     */
    function grantProviderRole(address account) public onlyAdmin {
        _grantRole(account, PROVIDER_ROLE);
        emit RoleGranted(account, PROVIDER_ROLE);
    }

    /**
     * @dev 撤销提供商角色（仅管理员）
     */
    function revokeProviderRole(address account) public onlyAdmin {
        _revokeRole(account, PROVIDER_ROLE);
        emit RoleRevoked(account, PROVIDER_ROLE);
    }

    // ====== 辅助函数 ======

    /**
     * @dev 覆盖自 ERC721 的 transferFrom 函数
     */
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public onlyAuthorizedOrProvider whenNotPaused {
        // 调用父合约的 transferFrom
        // 会自动触发 _beforeTokenTransfer 检查
        super.transferFrom(from, to, tokenId);
    }

    /**
     * @dev 覆盖自 ERC721 的 safeTransferFrom 函数
     */
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes calldata
    ) public onlyAuthorizedOrProvider whenNotPaused returns (bool) {
        // 调用父合约的 safeTransferFrom
        // 会自动触发 _beforeTokenTransfer 检查
        return super.safeTransferFrom(from, to, tokenId, calldata);
    }

    /**
     * @dev 获取所有者的列表（Gas 优化：使用枚举器）
     */
    function getAllOwners() public view returns (address[] memory) {
        // 获取所有 token 的所有者
        uint256[] memory tokenIds = new uint256[](totalSupply());
        address[] memory owners = new address[](totalSupply());
        uint256 ownerCount = 0;

        for (uint256 i = 0; i < totalSupply(); i++) {
            tokenIds[i] = i;
            address tokenOwner = ownerOf(i);
            
            // 检查是否已添加
            bool alreadyAdded = false;
            for (uint256 j = 0; j < ownerCount; j++) {
                if (owners[j] == tokenOwner) {
                    alreadyAdded = true;
                    break;
                }
            }
            
            if (!alreadyAdded) {
                owners[ownerCount] = tokenOwner;
                ownerCount++;
            }
        }

        return owners;
    }

    /**
     * @dev 获取用户的车辆列表
     * @param user 用户地址
     * @param limit 返回数量限制
     */
    function getUserCars(address user, uint256 limit) public view returns (uint256[] memory) {
        uint256[] memory userTokenIds = new uint256[](limit);
        uint256 count = 0;

        for (uint256 i = 0; i < totalSupply(); i++) {
            if (ownerOf(i) == user) {
                userTokenIds[count] = i;
                count++;
                if (count >= limit) {
                    break;
                }
            }
        }

        return userTokenIds;
    }

    /**
     * @dev 查询用户的车辆数量
     */
    function getUserCarCount(address user) public view returns (uint256) {
        uint256 balance = balanceOf(user);
        return balance;
    }

    // ====== 信息查询 ======

    /**
     * @dev 查询合约信息
     */
    function getContractInfo() public pure returns (
        string memory name,
        string memory symbol,
        uint8 decimals,
        uint256 totalSupply,
        uint256 paused,
        uint256 mintingPaused,
        uint256 ownerCars,
        address owner,
        bytes32 adminRole,
        bytes32 providerRole,
        address[] memory providers
    ) {
        return (
            name(),
            symbol(),
            decimals(),
            totalSupply(),
            paused() ? 1 : 0,
            _mintingPaused() ? 1 : 0,
            totalCars,
            owner(),
            DEFAULT_ADMIN_ROLE,
            PROVIDER_ROLE,
            super.getRoleMembers(PROVIDER_ROLE)
        );
    }
}
