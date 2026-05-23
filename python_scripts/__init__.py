def pretty_print_bytes(byte_amount: int) -> str:
	if byte_amount < 0:
		return pretty_print_bytes(abs(byte_amount))
	
	units: list[str] = ["B", "KiB", "MiB", "GiB", "TiB"]
	
	unit_index: int = 0
	
	while byte_amount > 1024:
		byte_amount = byte_amount / 1024
		unit_index += 1
	
	return f"{byte_amount:.1f} {units[unit_index]}"
