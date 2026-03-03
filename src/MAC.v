/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module MAC (
    input  wire [7:0] ui_in,    // Dedicated inputs [7:4] A [3:0] B 
    output wire [7:0] uo_out,   // Dedicated lower 8 output [7:0] 
    input  wire [7:0] uio_in,   // unused
    output wire [7:0] uio_out,  // Set to upper 8 output [15:8] 
    output wire [7:0] uio_oe,   // All bidr pins set to output 
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

reg  [15:0] accumulator;
wire [7:0] product;

assign product = ui_in[7:4] * ui_in[3:0];

always @(posedge clk) begin
    if (!rst_n) begin
        accumulator <= 16'b0;
    end else if (ena) begin
        accumulator <= accumulator + {8'b0, product};
    end
end


assign uo_out  = accumulator[7:0];     
assign uio_out = accumulator[15:8];

assign uio_oe  = 8'hFF;
//assign uio_in = 8'h00; 

// List all unused inputs to prevent warnings
wire _unused = &{uio_in, 1'b0};

endmodule
